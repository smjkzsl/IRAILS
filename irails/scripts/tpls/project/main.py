


from irails import  run as runserver ,generate_mvc_app 
app = generate_mvc_app()
if __name__=='__main__':
    runserver(app,debug=True)