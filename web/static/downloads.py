import sqlite3, sys, oscg

oscg.PFILE="downloads"
oscg.PAGE_TITLE="Downloads"
oscg.PAGE_DESC="Usage & Downloads"

oscg.print_header()

oscg.print_file("<center><img src=img/op-systems.png /><p></center>\n")

oscg.print_file(
"""
<p>Our sandboxed environment is perfect for running in a container, on bare metal,
or in the cloud environment of your choice.
Our optimized and secure static binaries run <nobr>EL-7+ & Amazon-Linux2+</nobr>,
&nbsp;<nobr>Ubuntu-18.04+ & Debian-10+,</nobr>&nbsp; <nobr>OSX-10.15+</nobr> &
<nobr>Windows 10+ <font color=red size=-0>(coming soon!)</font></nobr>

<p>&nbsp;
<table border=0 style='font-size:85%'>
<tr><td width=220 align=right><b>Installation:</b></td>
    <td width=375><input id=download type='text' size=78
      value = 'python3 -c "$(curl -fsSL https://oscg-io-download.s3.amazonaws.com/REPO/install.py)"' readonly='readonly' />
    </td>
    <td width=50><button onclick="myFunction('download')">Copy</button></td>
</tr>
<tr><td colspan=3>&nbsp;</td></tr>
<tr><td width=200 align=right><p><b>Usage sample:</b></td>
    <td width=375><input id=sample type='text' size=78
      value='cd oscg; ./io install pg14 --start' readonly='readonly' />
    </td>
    <td width=50><button onclick="myFunction('sample')">Copy</button></td>
</tr>
</table>

<p>&nbsp;
<table bgcolor=whitesmoke><tr><td>
<h4>Usage Notes:</h4>
<ul>
  <li>Install as a non-root user from your $HOME directory<br>&nbsp;</li>
  <li>Checkout our <a href="tutorial.html">tutorial</a> for more info on
      how to use the <code>oscg-io</code> CLI<br>&nbsp;</li>
  <li>We are tested with Python 2.7 & Python 3.6+&nbsp;&nbsp;
      You may substitute <code>python</code> or <code>python2</code> for 
      the <code>python3</code> in the above Installation command<br>&nbsp;
  </li>
  <li>In the near future you will be able to optionally install 
      via the command:<br><code>pip install oscg-io</code>
  </li>
</ul>

</td></tr></table>
"""
)

oscg.print_footer()

