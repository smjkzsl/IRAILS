


from irails import generate_mvc_app 
app = generate_mvc_app
if __name__=='__main__': 
    import uvicorn 
    app = generate_mvc_app()
    uvicorn.run(app,host="0.0.0.0",port=8000)
 