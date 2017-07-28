function validate_file(field, length, msg) {//video, 200*1024*1024, "视频大小不能超过200M"
	if (field.files.length == 0) {//可以在外面加上with(field),从而省略field.
		return true;
	}
	else if (field.files[0].size > length) {
		show_error(msg);
		return false;
	}
	else {
		return true;
	}
}
//validate_file和validate_file以及show_error写得很有用，没事干了回味回味
function check(thisform) {
	with (thisform) {
		if (!validate_required(video, "视频文件不能为空")) {
			video.focus();//聚焦函数，比如我做一个网页，里面有个文本框，想一开始鼠标就停留在文本框内
			return false
		}
		if (!validate_file(video, 300*1024*1024, "视频大小不能超过300M")) {
			video.focus();
			return false
		}
		if (!validate_file(cover, 3*1024*1024, "图像大小不能超过3M")) {
			cover.focus();
			return false
		}
		if (!validate_required(title, "标题不能为空")) {
			title.focus();
			return false
		}
		if (!validate_required(description, "描述不能为空")) {
			description.focus();
			return false
		}
		if (!validate_required(tag, "知识标签不能为空")) {
			tag.focus();
			return false
		}
		if (!validate_required(difficulty, "视频难度不能为空")) {
			difficulty.focus();
			return false
		}
	}
	return true;
}
