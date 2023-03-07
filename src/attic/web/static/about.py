import sqlite3, sys, oscg

oscg.PFILE="about"
oscg.PAGE_TITLE="About Us"
oscg.PAGE_DESC="About Us"

oscg.print_header()

oscg.print_file(
"""
&nbsp;<p>
Denis Lussier is the Founder & Chief Architect.  In 2004 Denis had the idea to add Oracle Compatibility to PostgreSQL
and he founded <a href="https://www.enterprisedb.com/why-edb/leave-oracle-for-postgresql-migration-postgres-move">EnterpriseDB</a>.
In 2009 Denis left EDB and founded OSCG Partners (OSCGP).  OSCGP had a consulting
subsidiary (OpenSCG) that specialized in
PostgreSQL and migrations from Oracle, SQL Server & MySQL.
In 2018 OSCGP sold OpenSCG to Amazon Web Services (AWS) and Denis moved to Seattle for a couple years.

<p>
In 2022 Denis started OSCG-IO as a new project for OSCGP. 
We're a small team featuring the two Principal Engineers,
<a href="https://www.linkedin.com/in/ahsan-hadi-6667608">Ahsan Hadi</a> &
<a href="https://www.linkedin.com/in/affansalman">Affan Salman</a>,
who led the effort to launch EDB in 2005 with it's Oracle compatibility for Postgres.  The 
rest of this story is still being written, stay tuned.

<p>
<center><a href="contact_us.html"><b>Contact OSCG</b></a></center>
"""
)

oscg.print_footer()

