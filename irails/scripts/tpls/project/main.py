import irails

if __name__=='__main__': 
    
    irails.core.run_server()
    
else:
    #for vercel like deploy
    app = irails.core.generate_mvc_app()