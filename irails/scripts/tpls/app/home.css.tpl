body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
}

header {
    background-color: #333;
    color: #fff;
    padding: 10px;
    text-align: center;
}

nav {
    background-color: #f2f2f2;
    padding: 10px;
    text-align: center;
    display: flex;
}

nav a {
    flex-direction: column;
    color: #333;
    text-decoration: none;
    padding: 10px;
}

section {
    padding: 10px;
    text-align: center;
}

footer {
    background-color: #333;
    color: #fff;
    padding: 10px;
    text-align: center;
}


/* Media Query for mobile devices */

@media only screen and (max-width: 600px) {
    header,
    nav,
    section,
    footer {
        padding: 5px;
    }
    nav a {
        font-size: 14px;
    }
}