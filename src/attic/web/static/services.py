import oscg

oscg.PFILE="services"
oscg.PAGE_TITLE="Services"
oscg.PAGE_DESC = "Services"

oscg.print_header()

oscg.print_file(
"""
&nbsp;<p>
We are the perfect company for your team to partner with.
Keep your developers focused on adding business value and we will collaboratively
and expertly supplement the team with a full range of database & development  services.
"""
)

oscg.print_file(
"""
<p>
<ul>
 <li>Migrating to Postgres<br>&nbsp;</li>
 <li>Application Migrations<br>&nbsp;</li>
 <li>Lift & Shift to the Cloud<br>&nbsp;</li>
 <li>Strategic Backend Software Development<br>&nbsp;</li>
 <li>Remote DBA Services<br>&nbsp;</li>
 <li>7x24 DBA & Application Support</li>
</ul>

<p>
<center><a href="contact_us.html"><b>Contact OSCG</b></a></center>
"""
)

oscg.print_footer()

