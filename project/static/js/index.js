// JavaScript Document

// Flip effects
window.onload = function() {
	var listBlue = document.getElementsByClassName('flipToBlue');
	var listOrange = document.getElementsByClassName('flipToOrange');
	i=listBlue.length;
	j=listOrange.length;
	while(i--){
		listBlue[i].className="span1 flipping_blue";
	}
	while(j--){
		listOrange[j].className="span1 flipping_orange";
	}
	window.setTimeout(flipped_blue,150)
}

function flipped_blue(){
	var listBlue = document.getElementsByClassName('flipping_blue');
	var listOrange = document.getElementsByClassName('flipping_orange');

	i=listBlue.length;
	j=listOrange.length;
	while(i--){
		listBlue[i].className="span1 flipped_blue";
	}
	while(j--){
		listOrange[j].className="span1 flipped_orange";
	}
}
