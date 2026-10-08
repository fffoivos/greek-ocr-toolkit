function showRecaptcha(filename, language) {
	grecaptcha.reset();
	document.getElementById('captcha_id').style.visibility = "visible";
        document.getElementById('error_captcha').innerHTML='';
	//document.getElementById('captcha_promt').style.visibility = "visible";
        document.getElementById('captcha_td').style.visibility = "visible";
        document.getElementById('submit_button_id').style.visibility = "visible";
	var loader = document.getElementById('dynamic_download');
	loader.innerHTML = '<div><form name="pdf_dump" target="_blank" action="'+tkl_docroot_portal+'/php/pdf_dump.php" method="post"><input type="hidden" name="filename" value="' + filename + '"/><input type="submit" style="visibility:hidden" name="go" id="hidden_download"/></form></div>';
	document.getElementById('submit_button_id').focus();
}