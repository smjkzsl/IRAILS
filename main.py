


from irails import generate_mvc_app 
app = generate_mvc_app
if __name__=='__main__': 
    import uvicorn
    from irails.config import config
    debug = config.get("debug",False)
    kwargs = {}
    if debug:
        apps_dirs = config.get('app').get("appdir")
        kwargs['reload'] = True
        kwargs['reload_dirs'] = apps_dirs
        kwargs['reload_includes'] = ['*.po']

    uvicorn.run("main:app",**kwargs)
    # runserver(app,debug=True)