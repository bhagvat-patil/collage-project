function login(){
let u=username.value,p=password.value,r=role.value;
if(r==="admin" && u==="admin" && p==="admin123"){
localStorage.setItem("role","admin");
location.href="dashboard.html";
}
else if(r==="user" && u && p){
localStorage.setItem("role","user");
location.href="dashboard.html";
}
else alert("Invalid Login");
}

function logout(){
localStorage.clear();
location.href="index.html";
}
