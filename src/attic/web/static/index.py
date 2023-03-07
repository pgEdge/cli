import sqlite3, sys, oscg

oscg.PFILE="index"
oscg.PAGE_TITLE="Datastore Ops Framework"
oscg.PAGE_DESC="OSCG: The Datastore Operations Framework"

oscg.print_header()

oscg.print_file(
"""
&nbsp;<p>
OSCG-IO is an Open Source cross-platform installation, configuration &
 operations framework for datastores.
We fully embrace core PostgreSQL and its extensive collection
of enterprise-class community extensions.
We understand that the Postgres worldwide takeover may never be complete,
so we support other datastores as well.

<center><img src=img/op-systems.png /></center>



<p>&nbsp;
<table border=0 style='font-size:85%'>
<tr><td width=220 align=right><b>Installation:</b></td>
    <td width=375><input style="background-color:GhostWhite" id=download type='text' size=78
      value = 'python3 -c "$(curl -fsSL https://oscg-io-download.s3.amazonaws.com/REPO/install.py)"' readonly='readonly' />
    </td>
    <td width=50><button onclick="myFunction('download')">Copy</button></td>
</tr>
</table>

<p>&nbsp;
<center>
<div class="container-fluid">
<h5>Flexible Deployment Options</h5>
<ul class="nav nav-pills">
  <li class="nav-item">
    <a class="nav-link active" aria-current="page" href="#">Public Cloud</a>
  </li>
  <li class="nav-item">
    <a class="nav-link" href="#">Multi-cloud</a>
  </li>
  <li class="nav-item">
    <a class="nav-link" href="#">Private cloud</a>
  </li>
  <li class="nav-item">
    <a class="nav-link href="#">Hybrid Cloud</a>
  </li>
  <li class="nav-item">
    <a class="nav-link href="#">On-Prem</a>
  </li>
</ul>
</div>
</center>

"""
)

oscg.print_footer()

