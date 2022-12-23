import sqlite3, sys, oscg

oscg.PFILE="tutorial"
oscg.PAGE_TITLE="Tutorial"
oscg.PAGE_DESC="Tutorial"

oscg.print_header()

oscg.print_file(
"""
<p>
<h4>1.) Review the help file</h4>

Get into the <code>oscg</code> base directory at the command line.
<p>Now run the <code>help</code> command to see that things are as expected
<pre>

   <font size=+1>$ ./io help</font>

      <b>Usage:</b> io command [component1 component2 ...]

      <b>Available commands:</b>
        <b>help</b>       - Show this help file
        <b>info</b>       - Display OS or component information
        <b>list</b>       - Display installed & available components 
        <b>status</b>     - Display status of installed server components 
        <b>start</b>      - Start server components
        <b>stop</b>       - Stop server components
        <b>enable</b>     - Enable a server component
        <b>disable</b>    - Disable a server component from starting automatically
        <b>update</b>     - Retrieve new list of available components
        <b>upgrade</b>    - Upgrade installed components to newer (compatible) versions
        <b>install</b>    - Install a component  

</pre>


<br>
<h4>2.) Demonstrate the <code>io</code> command line environment.</h4>

The <code>info</code> command lists information about the OS or a component
<pre>
   <font size=+1>$ ./io info</font>

      <b>User & Host:</b> denisl  localhost  127.0.0.1
      <b>         Os:</b> Mac OS X 12.4 x64
      <b>   Hardware:</b> 16 GB, 8 x Intel Core i7-2820QM @ 2.30GHz


   <font size=+1>$ ./io info pg14</font>

      <b>  Project:</b> pg (http://postgresql.org)
      <b>Component:</b> pg14  14.3 (linux64, osx64, win64)
      <b>      Doc:</b> http://www.postgresql.org/docs/14/

</pre>

<p>The <code>list</code> command displays installed and available components.  It confirms
that only the core<br> Postgres server component, in this case <code>pg14</code>, is installed
and enabled by default.
<pre>
   <font size=+1>$ ./io list</font>

        <b>Component     Version       Port    Status      
        ------------  ------------  ------  ------------</b>
        pg11          11.16                 Not Installed   
        pg12          12.11                 Not Installed   
        pg13          13.7                  Not Installed   
        pg14          14.3          5432    Installed   
</pre>

<br>
The <code>status</code> command confirms whether server components are listening on
their assigned ports.
<pre>     
   <font size=+1>$ ./io status</font>

       pg14    stopped on port 5432
</pre>

<br>
The <code>start</code> command will start up whatever servers are installed (in this case pg14)
<pre>     
   <font size=+1>$ ./io start</font>

       pg14 starting...
</pre>

<br>
Running the <code>status</code> command displays information about installed server components.
<pre>     
   <font size=+1>$ ./io status</font>

       pg14 running on port 5432
</pre>

Now lets use the <code>stop</code> command to shutdown postgres.
<pre>     
   <font size=+1>$ ./io stop</font>

       pg14 stopping...
</pre>

<br>
<h4>3.) Install additional components</h4>

Use the <code>install</code> command to provision additional components such as <code>pg12</code>.
Using the "--start" option will install and then start PG with the default passwd = 'password'.  Because port 5432
was in use, we automagically start on port 5433.
<pre>
   <font size=+1>$ ./io install pg12 --start</font>

        Get:2 pg12-12.11-amd
          Unpacking pg12-12.11-amd.tar.bz2
          pg12 Installed & Started


   <font size=+1>$ ./io list</font>

        Component     Version    Port    Status      
        ------------  --------  ------  ------------
        pg11          11.16              Not Installed                       
        pg12          12.11      5433    Installed   
        pg13          13.7               Not Installed
        pg14          14.3       5432    Installed   

</pre>

We now run the status command to confirm that both the PG servers are installed.
<pre>
   <font size=+1>$ ./io status</font>

        pg12 (Started on port 5433)
        pg14 (Stopped on port 5432)
</pre>

<br>
The <code>start</code> command is used to start back up PostgreSQL 14
<pre>
   <font size=+1>$ ./io start pg14</font>

       pg14 starting...
</pre>

<br>
Running the <code>status</code> command displays information about installed server components.
<pre>     
   <font size=+1>$ ./io status</font>

       pg12  (Running on port 5433)
       pg14  (Running on port 5432)
</pre>
"""
)

oscg.print_footer()
