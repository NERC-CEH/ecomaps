<html>
<body>
  <p>
    <form action="/account/dologin?came_from=${came_from}" method="POST">
      Username: ${h.html_tags.text('login')}
      <br />
      Password: ${h.html_tags.password('password')}
      <br />
      <input type="submit" value="Login" />
    </form>
  </p>
<p>${message}</p>
</body>
</html>