from source.env import DEBUG
from quart import Response, request, current_app
from werkzeug.exceptions import HTTPException
from typing import Any, List
import logging


logger = logging.getLogger('api_helper')


class ArgumentSanitizationError(Exception):
    """
    Exception raised when an error occured in parsing arguments for an API method.

    """
    pass


class ArgumentValidationError(Exception):
    """
    Exception raised when an error occured while running a custom argument validator.

    """
    pass


def _sanitize_arguments(argument_rules : dict, arguments : dict):
    """
    Sanetizes arguments based on a specified ruleset.
    
    Possible argument rules:
    'optional' (bool):
        Specifies wether this argument is required. If it is, ArgumentSanitizationError will be raised when it's missing.
    'allowed_types' (list[type]):
        List of allowed type.
        If specified, ArgumentSanitizationError will be raised if the provided type doesn't match the list of allowed types.
    'transformer' (callable):
        A callable that will be invoked on the value for this argument.
    'validator' (callable):
        A callable that will be invoked on the value for this argument (after transformer if provided).
        Callable should raise ArgumentValidationError with a message provided as validation error reason if the argument isn't acceptable.
    'allowed_values' (list[Any]):
        List of allowed values.
        If specified, ArgumentSanitizationError will be raised if the value (after transformer if provided) isn't in the list of allowed values.
    'arguments' (dict):
        List of nested argument rules.

    """
    def _sanitize_argument_recursive(root_element: dict, argument_rule : dict, argument_name: str, path: List[str], obj: dict):
        rule_optional = argument_rule.get('optional', None)
        rule_allowed_types = argument_rule.get('allowed_types', None)
        rule_transformer = argument_rule.get('transformer', None)
        rule_validator = argument_rule.get('validator', None)
        rule_allowed_values = argument_rule.get('allowed_values', None)
        rule_arguments = argument_rule.get('arguments', None)

        # If argument is required but not provided, raise ArgumentSanitizationError
        # If argument is optional and not provided, return
        if argument_name not in root_element.keys():
            if rule_optional: return
            argument_path = '.'.join(path)
            raise ArgumentSanitizationError(f"Missing required argument '{argument_name}' at '{argument_path}'.")

        # Fetch the argument value and validate type
        argument_value : Any = root_element[argument_name]
        if rule_allowed_types and type(argument_value) not in rule_allowed_types:
            argument_path = '.'.join(path)
            argument_type = type(argument_value).__name__
            allowed_types = ', '.join([ t.__name__ for t in rule_allowed_types ])
            raise ArgumentSanitizationError(f"Unsupported type for argument '{argument_name}' at '{argument_path}': {argument_type}. Allowed type(s): {allowed_types}")

        # If transformer function is specified, apply to argument value
        # No custom exception handling here, as any error should lead to an internal server error.
        if rule_transformer:
            argument_value = rule_transformer(argument_value)
        
        # If custom validator function is specified, run for argument value
        # When validation fails, output reason. When any other exception happens, it should lead to an internal server error.
        if rule_validator:
            try:
                rule_validator(argument_value)
            except ArgumentValidationError as ex:
                argument_path = '.'.join(path)
                raise ArgumentSanitizationError(f"Validation for argument '{argument_name}' at '{argument_path}' failed: {str(ex)}")
        
        # If allowed values list is specified but argument value isn't on it, raise ArgumentSanitizationError
        if rule_allowed_values and argument_value not in rule_allowed_values:
            argument_path = '.'.join(path)
            allowed_values = ', '.join([ f"'{v}'" for v in rule_allowed_values ])
            raise ArgumentSanitizationError(f"Unsupported value for argument '{argument_name}' at '{argument_path}': '{argument_value}'. Allowed value(s): {allowed_values}")

        if rule_arguments:
            # Add empty dict to target object and process all specified sub-arguments recursively
            obj[argument_name] = {}
            for sub_argument_name, sub_argument_rule in rule_arguments.items():
                _sanitize_argument_recursive(argument_value, sub_argument_rule, sub_argument_name, path + [argument_name], obj[argument_name])
        
        else:
            # Append the argument value to the target object
            obj[argument_name] = argument_value

    sanitized = {}
    for argument_name, argument_rule in argument_rules.items():
        _sanitize_argument_recursive(arguments, argument_rule, argument_name, ['root'], sanitized)
    return sanitized


def api_method(argument_rules : dict = {}, sanitize_arguments : bool = True):
    """
    Decorator to specify some common behaviors for API methods.
    The arguments parameter specifies which arguments the API method specified.
    If sanitize_arguments = True (default), the JSON request arguments will be
    processed by _sanitize_arguments before passing them through to the wrapped function.
    That way, any arguments the client sends that aren't part of the API provided argument
    rules will be discarded.

    """
    def decorator(func):
        async def wrapper():
            try:
                arguments = _sanitize_arguments(argument_rules, await request.get_json()) if sanitize_arguments else await request.get_json()
                response_status, response_data = await func(arguments)
                return Response(current_app.json.dumps({ 'status': response_status, 'data': response_data }) + '\n', status=response_status, mimetype='application/json')
            
            except ArgumentSanitizationError as ex:
                    # Exception in client provided arguments
                    logger.exception(f"Exception during sanitization of arguments for API method '{getattr(func, '__name__', 'Unkown')}!")
                    error_message = f"400 Bad Request: {str(ex)}"
                    return Response(current_app.json.dumps({ 'status': 400, 'data': { 'error': error_message } }) + '\n', status=400, mimetype='application/json')

            except HTTPException as ex:
                # Werkzeug HTTP Exception
                logger.exception(f"HTTP Exception during processing of API method '{getattr(func, '__name__', 'Unkown')}!")
                error_message = f"{ex.code} {ex.name}: {ex.description}"
                return Response(current_app.json.dumps({ 'status': ex.code, 'data': { 'error': error_message } }) + '\n', status=ex.code, mimetype='application/json')

            except Exception as ex:
                # Any other exception, probably in our code
                logger.exception(f"Exception during processing of API method '{getattr(func, '__name__', 'Unkown')}'!")
                error_message = f"500 Internal Server Error: {str(ex)}" if DEBUG else "500 Internal Server Error"
                return Response(current_app.json.dumps({ 'status': 500, 'data': { 'error': error_message } }) + '\n', status=500, mimetype='application/json')

        # NOTE: The __name__ attribute of the decorated function is used by flask.sansio.scaffhold.py in _endpoint_from_view_func 
        #       to identify the decorated function, it has to be unique. Since we're decorating the decorated function, pass the name through.
        wrapper.__name__ = func.__name__

        return wrapper
    return decorator