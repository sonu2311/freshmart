
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
