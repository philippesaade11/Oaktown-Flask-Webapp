token = localStorage.getItem("token");
username = localStorage.getItem("username");
password = localStorage.getItem("password");

function checkLogin(){
    if(token == null){
    	window.location = "/login";
    }
    $.ajax({
        url: "http://lehfedcountry.pythonanywhere.com/checkToken",
        type: "POST",
    	headers: {
    		"x-access-token": token
    	},
    	success: function(data){
            username = data;
    	},
    	error: function(data){
    	    if(username != "" && username != null && password != null && password != ""){
    	        login(username, password);
    	    } else {
    	        window.location = "/login";
    	    }
    	},
    	async: false
    });
}

function login(user, pass){
    $.ajax({
        url: "http://lehfedcountry.pythonanywhere.com/login",
        type: "POST",
        headers: {
            "Authorization": "Basic " + btoa(user + ":" + pass)
        },
        success: function(data){
            localStorage.setItem("token", data.token);
            localStorage.setItem("username", user);
            localStorage.setItem("password", pass);
            username = user;
            password = pass;
            token = data.token;
			window.location = "/";
        },
		error: function(data){
    	    window.location = "/login";
		},
		async: false
    });
}

function logout(){
    token = "";
    username = "";
    password = "";
	localStorage.setItem("token", "");
	localStorage.setItem("username", "");
	localStorage.setItem("password", "");
    window.location = "/login";
}