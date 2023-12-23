import irails

if __name__=='__main__': 
    
    irails.core.run_server()
else:
    app = irails.core.generate_mvc_app()
    
 