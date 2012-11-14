<!DOCTYPE html>
<html>
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
	<title>Server usage</title>
	<style>
/*to make all 4 plots fall in one line*/
body{
	width: 2000px;
}
	</style>
</head>
<body>
<?php
error_reporting (E_ALL);

$files = array();

$dh = opendir("hour");
while(true)
{
	$file = readdir($dh);
	if($file === false)
		break;
	if($file == ".")
		continue;
	if($file == "..")
		continue;
	if($file == "index.php")
		continue;

	$files[] = $file;
}

sort($files);

foreach($files as $file)
{
	echo '<div>';
	echo '<img src="hour/'.$file.'"/>';
	echo '<img src="day/'.$file.'"/>';
	echo '<img src="week/'.$file.'"/>';
	echo '<img src="month/'.$file.'"/>';
	echo '</div>';
}

?>
</body>
</html>
