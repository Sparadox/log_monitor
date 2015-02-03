=== Traffic monitor ===

This very minimalistic Python application is intented to monitor traffic on a server of yours by watching the access_log file. It's compliant with Apache's standard access log format.

Feel free to extend the LogParser class and wire your new class in the MainMonitor class to have it work with any different log file format. 

=== Development status ===

At the moment the app is extremely minimalistic. You can open the README.pdf file to have more information about what it does. 

It is just an app I wrote in a couple of hours as part of a test for an application. Though, it is rather modular and can easily be used as a base to make something more interesting. It's written in Python, already highly customizable, rather light and it could run as a deamon on your server.

Feel free to clone it, fork it, make pull requests or ask me questions about it...

=== Possible improvements ===

* Replace the MonitorGUI class with a RESTful server app (using the basic Python http.server for instance along with an authentication mecanism) or directly a (protected) web-interface to monitor your traffic from a remote location without having to use SSH.

* Add other submonitors to keep track of all requests (in particular, the failing requests throwing a 4xx or 5xx HTTP response code) and figure out how you could fix your website's routes to avoid your users getting 404 errors...

* Store all the traffic history ON HDD (in general, avoid any operation that could overload the RAM, your server doesn't need it...). A SQLite DB would be an excellent start, if you need to make complex queries on it, it is still very straightforward to import the data in a PostgreSQL, Hive/Hadoop or whatever system you want to perform performance demanding operation on your history.
