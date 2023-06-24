import types

from aiogram import Dispatcher

from app.exceptions import RegisterHandlerError


def register(dp: Dispatcher, *handlers: types.ModuleType) -> None:
    """
    Handlers registering. If `register()` wasn't implemented in module,
    it skips with error log message.
    :param handlers: .py handler-modules with implemented register() method.
    :param dp: Dispatcher.
    """

    for handler in handlers:
        routers = []
        if isinstance(handler, types.ModuleType):
            try:
                routers.append(handler.register())
            except AttributeError as error:
                raise RegisterHandlerError(
                    f"register() method wasn't implemented "
                    f"in {str(error.obj)}"
                )
        else:
            raise RegisterHandlerError(
                f"`{handler}` from submitted args to `register()` "
                f"is not a module"
            )
        dp.include_routers(*routers)
