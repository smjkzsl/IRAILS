<!DOCTYPE html>
<html>

<head>
    <meta charset="utf-8">
    <title>${app_name}-Home</title>
    <link rel="stylesheet" href="home.css" />

</head>

<body>
    <header style="text-align:left;display: flex;">
        <h1>Python</h1>
        <h4>on FastApi</h4>

    </header>
    <nav>
        {% for item in routers_map %} 
            {% if 'GET' in routers_map[item]['methods'] %} 
                {% if routers_map[item]['auth']=='none' or request.session['user'] %}
        <a href="${routers_map[item]['path']}">
            ${routers_map[item]['doc'] and routers_map[item]['doc']['title'] or item}
        </a> 
                {% endif %} 
            {% endif %} 
        {% endfor %}
 
        {% if request.session['user'] %}
            <a href="/user/logout">
            <b> ${request.session['user']['username']} </b> Logout</a> 
        {% endif %}
    </nav>
    <section>
        <h2>Welcome to my website</h2>
        <p>This is an example of a responsive design that works well on both desktop and mobile devices.</p>
        <p>here is the `text` variable in class method:${text}</p>
        <p style="color:red"><b>${flash}</b></p>
    </section>
    <footer>
        <p>&copy; 2023 My Website</p>
    </footer>
</body>

</html>