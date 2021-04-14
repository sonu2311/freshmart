
var url_params = new URLSearchParams((new URL(window.location.href)).search)

var trimUndesiredFields = function(obj) {
  if (obj && obj.constructor === Object) {
    var output = {}
    for (var k in obj) {
      if (k.length == 0 || k[0] != '$') {
        output[k] = trimUndesiredFields(obj[k])
      }
    }
    return output
  } else if (obj instanceof Array) {
    var output = []
    for (var k in obj) {
      output.push(trimUndesiredFields(obj[k]))
    }
    return output
  } else {
    return obj
  }
}

var store_key = "freshmart_"

function getter(key) {
  key = store_key + key
  if (localStorage[key] === undefined) {
    return null
  } else {
    return JSON.parse(localStorage[key])
  }
}

function setter(key, value) {
  key = store_key + key
  if (value) {
    localStorage[key] = JSON.stringify(trimUndesiredFields(value))
  } else {
    console.error("Invalid data stored")
  }
}

function load() {
  return getter("main")
}

function store(data) {
  setter("main", data)
}

function clear(key) {
  key = key || "main"
  localStorage.removeItem(store_key + key)
}

var session = getter("session") || {}

var clear_session = function() {
  clear("session")
  session = {}
}

var api = function(http, api_url, input, callback) {
  input = input || {}
  input.session = session
  return http({
    method: "POST",
    url: api_url,
    headers: {'Content-Type': 'application/json'},
    data: input}).then(callback ? function(d) {
      console.log(d)
        session = d.data.session || session;
        setter("session", session)
        callback(d.data.data)
      } : callback);
}

var Is_login=function(){
  if(("login_key" in session) && ("id" in session["login_key"])){
    return true
  }
  else{
    return false
  }
}

var getLoginId=function(){
  if(("login_key" in session) && ("id" in session["login_key"])){
    return session["login_key"]["id"]
  }
  else{
    return 0
  }
}

// jo bi is vakt login h uska role btayega ye fuction. 
// agr abi farmer login h to output FARMER ayega.
var Login_Role=function(){
  if(("login_key" in session) && ("role" in session["login_key"])){
    return session["login_key"]["role"]
  }
  else{
    return null
  }
}

var app = angular.module('myApp', [])

app.controller('common_ctrl', function($scope, $timeout) {
  var cleanup=function(){
    var cleanup_list=[]
    for (i in $scope.messages){
      if ((new Date().getTime()) < $scope.messages[i]["deadline"]){

        cleanup_list.push($scope.messages[i])
      }
    }
    $scope.messages=cleanup_list
  }
  $scope.messages=[]
  $scope.my_alert = function(y, timeout) {
    timeout = timeout || 4000  // ms.
    $scope.messages.push({"message":y, "deadline": new Date().getTime() + timeout})
    $timeout(cleanup, timeout)
  }

})



app.controller('ctrl_header', function($scope) {
  $scope.profile_name = Is_login() ? session.login_key.name : "Not login"
  $scope.is_login = Is_login()
  $scope.role = Login_Role()

  $scope.header = $scope

  $scope.logout = function() {
    clear_session()
    window.location.href = "index.html"
  }

  var url_params = new URLSearchParams((new URL(window.location.href)).search)
  $scope.p = url_params.get("sort_price") || ""

  $scope.search_key = ""
  $scope.search=function(){
    console.log(3333)
    window.location.href = "product_page.html?search_key=" + $scope.search_key + "&sort_price="+$scope.p
  }
 
  $scope.open_menu=false

  $scope.menu_close_open=function(){
    console.log(11)
    $scope.open_menu =!$scope.open_menu
  }

})