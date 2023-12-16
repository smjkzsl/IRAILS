from functools import update_wrapper
import os
import sys
from typing import Dict
import click
import irails
from fastapi.testclient import TestClient

setattr(irails.application,'__name__',"irails.application.shell")
from irails.database import Service

def create_context()->Dict:
    ctx = {}
    test_client = TestClient(app = irails.application )
  
    ctx.update({'app':irails.application,
                'service':Service,
                'client':test_client})

    return ctx
def shell_command() -> None:
    """Run an interactive Python shell in the context of a given
    irails application.  The application will populate the default
    namespace of this shell according to its configuration.

    This is useful for executing small snippets of management code
    without having to manually configure the application.
    """
    import code
     
    irails.generate_mvc_app('shell')
    banner = (
        f"Python {sys.version} on {sys.platform}\n" 
        f"Env: IRails {irails.__version__} on {irails.application.title}"
    )
     
    ctx = create_context()
    # Support the regular Python interpreter startup script if someone
    # is using it.
    startup = os.environ.get("PYTHONSTARTUP")
    if startup and os.path.isfile(startup):
        with open(startup) as f:
            eval(compile(f.read(), startup, "exec"), ctx)

    
    
    # Site, customize, or startup script can set a hook to call when
    # entering interactive mode. The default one sets up readline with
    # tab and history completion.
    interactive_hook = getattr(sys, "__interactivehook__", None)

    if interactive_hook is not None:
        try:
            import readline
            from rlcompleter import Completer
        except ImportError:
            pass
        else:
            # rlcompleter uses __main__.__dict__ by default, which is
            # irails.__main__. Use the shell context instead.
            readline.set_completer(Completer(ctx).complete)

        interactive_hook()

    code.interact(banner=banner, local=ctx)

def main():
    from irails.config import IS_IN_irails
    if not IS_IN_irails:
        print("Please run this in irails project dir.")
        exit(0)
    shell_command()