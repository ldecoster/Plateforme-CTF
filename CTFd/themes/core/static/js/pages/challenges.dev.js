/******/ (function(modules) { // webpackBootstrap
/******/ 	// install a JSONP callback for chunk loading
/******/ 	function webpackJsonpCallback(data) {
/******/ 		var chunkIds = data[0];
/******/ 		var moreModules = data[1];
/******/ 		var executeModules = data[2];
/******/
/******/ 		// add "moreModules" to the modules object,
/******/ 		// then flag all "chunkIds" as loaded and fire callback
/******/ 		var moduleId, chunkId, i = 0, resolves = [];
/******/ 		for(;i < chunkIds.length; i++) {
/******/ 			chunkId = chunkIds[i];
/******/ 			if(installedChunks[chunkId]) {
/******/ 				resolves.push(installedChunks[chunkId][0]);
/******/ 			}
/******/ 			installedChunks[chunkId] = 0;
/******/ 		}
/******/ 		for(moduleId in moreModules) {
/******/ 			if(Object.prototype.hasOwnProperty.call(moreModules, moduleId)) {
/******/ 				modules[moduleId] = moreModules[moduleId];
/******/ 			}
/******/ 		}
/******/ 		if(parentJsonpFunction) parentJsonpFunction(data);
/******/
/******/ 		while(resolves.length) {
/******/ 			resolves.shift()();
/******/ 		}
/******/
/******/ 		// add entry modules from loaded chunk to deferred list
/******/ 		deferredModules.push.apply(deferredModules, executeModules || []);
/******/
/******/ 		// run deferred modules when all chunks ready
/******/ 		return checkDeferredModules();
/******/ 	};
/******/ 	function checkDeferredModules() {
/******/ 		var result;
/******/ 		for(var i = 0; i < deferredModules.length; i++) {
/******/ 			var deferredModule = deferredModules[i];
/******/ 			var fulfilled = true;
/******/ 			for(var j = 1; j < deferredModule.length; j++) {
/******/ 				var depId = deferredModule[j];
/******/ 				if(installedChunks[depId] !== 0) fulfilled = false;
/******/ 			}
/******/ 			if(fulfilled) {
/******/ 				deferredModules.splice(i--, 1);
/******/ 				result = __webpack_require__(__webpack_require__.s = deferredModule[0]);
/******/ 			}
/******/ 		}
/******/ 		return result;
/******/ 	}
/******/
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// object to store loaded and loading chunks
/******/ 	// undefined = chunk not loaded, null = chunk preloaded/prefetched
/******/ 	// Promise = chunk loading, 0 = chunk loaded
/******/ 	var installedChunks = {
/******/ 		"pages/challenges": 0
/******/ 	};
/******/
/******/ 	var deferredModules = [];
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, { enumerable: true, get: getter });
/******/ 		}
/******/ 	};
/******/
/******/ 	// define __esModule on exports
/******/ 	__webpack_require__.r = function(exports) {
/******/ 		if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 			Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 		}
/******/ 		Object.defineProperty(exports, '__esModule', { value: true });
/******/ 	};
/******/
/******/ 	// create a fake namespace object
/******/ 	// mode & 1: value is a module id, require it
/******/ 	// mode & 2: merge all properties of value into the ns
/******/ 	// mode & 4: return value when already ns object
/******/ 	// mode & 8|1: behave like require
/******/ 	__webpack_require__.t = function(value, mode) {
/******/ 		if(mode & 1) value = __webpack_require__(value);
/******/ 		if(mode & 8) return value;
/******/ 		if((mode & 4) && typeof value === 'object' && value && value.__esModule) return value;
/******/ 		var ns = Object.create(null);
/******/ 		__webpack_require__.r(ns);
/******/ 		Object.defineProperty(ns, 'default', { enumerable: true, value: value });
/******/ 		if(mode & 2 && typeof value != 'string') for(var key in value) __webpack_require__.d(ns, key, function(key) { return value[key]; }.bind(null, key));
/******/ 		return ns;
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "/themes/core/static/js";
/******/
/******/ 	var jsonpArray = window["webpackJsonp"] = window["webpackJsonp"] || [];
/******/ 	var oldJsonpFunction = jsonpArray.push.bind(jsonpArray);
/******/ 	jsonpArray.push = webpackJsonpCallback;
/******/ 	jsonpArray = jsonpArray.slice();
/******/ 	for(var i = 0; i < jsonpArray.length; i++) webpackJsonpCallback(jsonpArray[i]);
/******/ 	var parentJsonpFunction = oldJsonpFunction;
/******/
/******/
/******/ 	// add entry module to deferred list
/******/ 	deferredModules.push(["./CTFd/themes/core/assets/js/pages/challenges.js","helpers","vendor","default~pages/challenges~pages/main~pages/notifications~pages/settings~pages/setup~pages/stats"]);
/******/ 	// run deferred modules when ready
/******/ 	return checkDeferredModules();
/******/ })
/************************************************************************/
/******/ ({

/***/ "./CTFd/themes/core/assets/js/pages/challenges.js":
/*!********************************************************!*\
  !*** ./CTFd/themes/core/assets/js/pages/challenges.js ***!
  \********************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

;
eval("\n\n__webpack_require__(/*! ./main */ \"./CTFd/themes/core/assets/js/pages/main.js\");\n\n__webpack_require__(/*! bootstrap/js/dist/tab */ \"./node_modules/bootstrap/js/dist/tab.js\");\n\nvar _regeneratorRuntime = _interopRequireDefault(__webpack_require__(/*! regenerator-runtime */ \"./node_modules/regenerator-runtime/runtime.js\"));\n\nvar _ezq = __webpack_require__(/*! ../ezq */ \"./CTFd/themes/core/assets/js/ezq.js\");\n\nvar _utils = __webpack_require__(/*! ../utils */ \"./CTFd/themes/core/assets/js/utils.js\");\n\nvar _moment = _interopRequireDefault(__webpack_require__(/*! moment */ \"./node_modules/moment/moment.js\"));\n\nvar _jquery = _interopRequireDefault(__webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\"));\n\nvar _CTFd = _interopRequireDefault(__webpack_require__(/*! ../CTFd */ \"./CTFd/themes/core/assets/js/CTFd.js\"));\n\nvar _config = _interopRequireDefault(__webpack_require__(/*! ../config */ \"./CTFd/themes/core/assets/js/config.js\"));\n\nfunction _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { \"default\": obj }; }\n\nfunction asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) { try { var info = gen[key](arg); var value = info.value; } catch (error) { reject(error); return; } if (info.done) { resolve(value); } else { Promise.resolve(value).then(_next, _throw); } }\n\nfunction _asyncToGenerator(fn) { return function () { var self = this, args = arguments; return new Promise(function (resolve, reject) { var gen = fn.apply(self, args); function _next(value) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, \"next\", value); } function _throw(err) { asyncGeneratorStep(gen, resolve, reject, _next, _throw, \"throw\", err); } _next(undefined); }); }; }\n\n_CTFd[\"default\"]._internal.challenge = {};\nvar challenges = [];\nvar solves = [];\nvar tagList = [];\n\nvar loadChal = function loadChal(id) {\n  var chal = _jquery[\"default\"].grep(challenges, function (chal) {\n    return chal.id == id;\n  })[0];\n\n  if (chal.state === \"hidden\") {\n    (0, _ezq.ezAlert)({\n      title: \"Challenge Hidden!\",\n      body: \"You haven't unlocked this challenge yet!\",\n      button: \"Got it!\"\n    });\n    return;\n  }\n\n  displayChal(chal);\n};\n\nvar loadChalByName = function loadChalByName(name) {\n  var idx = name.lastIndexOf(\"-\");\n  var pieces = [name.slice(0, idx), name.slice(idx + 1)];\n  var id = pieces[1];\n\n  var chal = _jquery[\"default\"].grep(challenges, function (chal) {\n    return chal.id == id;\n  })[0];\n\n  displayChal(chal);\n};\n\nvar displayChal = function displayChal(chal) {\n  return Promise.all([_CTFd[\"default\"].api.get_challenge({\n    challengeId: chal.id\n  }), _jquery[\"default\"].getScript(_config[\"default\"].urlRoot + chal.script), _jquery[\"default\"].get(_config[\"default\"].urlRoot + chal.template)]).then(function (responses) {\n    var challenge = _CTFd[\"default\"]._internal.challenge;\n    (0, _jquery[\"default\"])(\"#challenge-window\").empty(); // Inject challenge data into the plugin\n\n    challenge.data = responses[0].data; // Call preRender function in plugin\n\n    challenge.preRender(); // Build HTML from the Jinja response in API\n\n    (0, _jquery[\"default\"])(\"#challenge-window\").append(responses[0].data.view);\n    (0, _jquery[\"default\"])(\"#challenge-window #challenge-input\").addClass(\"form-control\");\n    (0, _jquery[\"default\"])(\"#challenge-window #challenge-submit\").addClass(\"btn btn-md btn-outline-secondary float-right\");\n    var modal = (0, _jquery[\"default\"])(\"#challenge-window\").find(\".modal-dialog\");\n\n    if (window.init.theme_settings && window.init.theme_settings.challenge_window_size) {\n      switch (window.init.theme_settings.challenge_window_size) {\n        case \"sm\":\n          modal.addClass(\"modal-sm\");\n          break;\n\n        case \"lg\":\n          modal.addClass(\"modal-lg\");\n          break;\n\n        case \"xl\":\n          modal.addClass(\"modal-xl\");\n          break;\n\n        default:\n          break;\n      }\n    }\n\n    (0, _jquery[\"default\"])(\".challenge-solves\").click(function (_event) {\n      getSolves((0, _jquery[\"default\"])(\"#challenge-id\").val());\n    });\n    (0, _jquery[\"default\"])(\".nav-tabs a\").click(function (event) {\n      event.preventDefault();\n      (0, _jquery[\"default\"])(this).tab(\"show\");\n    }); // Handle modal toggling\n\n    (0, _jquery[\"default\"])(\"#challenge-window\").on(\"hide.bs.modal\", function (_event) {\n      (0, _jquery[\"default\"])(\"#challenge-input\").removeClass(\"wrong\");\n      (0, _jquery[\"default\"])(\"#challenge-input\").removeClass(\"correct\");\n      (0, _jquery[\"default\"])(\"#incorrect-key\").slideUp();\n      (0, _jquery[\"default\"])(\"#correct-key\").slideUp();\n      (0, _jquery[\"default\"])(\"#already-solved\").slideUp();\n      (0, _jquery[\"default\"])(\"#too-fast\").slideUp();\n    });\n    (0, _jquery[\"default\"])(\".load-hint\").on(\"click\", function (_event) {\n      loadHint((0, _jquery[\"default\"])(this).data(\"hint-id\"));\n    });\n    (0, _jquery[\"default\"])(\"#challenge-submit\").click(function (event) {\n      event.preventDefault();\n      (0, _jquery[\"default\"])(\"#challenge-submit\").addClass(\"disabled-button\");\n      (0, _jquery[\"default\"])(\"#challenge-submit\").prop(\"disabled\", true);\n\n      _CTFd[\"default\"]._internal.challenge.submit().then(renderSubmissionResponse).then(loadChals).then(markSolves);\n    });\n    (0, _jquery[\"default\"])(\"#challenge-input\").keyup(function (event) {\n      if (event.keyCode == 13) {\n        (0, _jquery[\"default\"])(\"#challenge-submit\").click();\n      }\n    });\n    challenge.postRender();\n    window.location.replace(window.location.href.split(\"#\")[0] + \"#\".concat(chal.name, \"-\").concat(chal.id));\n    (0, _jquery[\"default\"])(\"#challenge-window\").modal();\n  });\n};\n\nfunction renderSubmissionResponse(response) {\n  var result = response.data;\n  var result_message = (0, _jquery[\"default\"])(\"#result-message\");\n  var result_notification = (0, _jquery[\"default\"])(\"#result-notification\");\n  var answer_input = (0, _jquery[\"default\"])(\"#challenge-input\");\n  result_notification.removeClass();\n  result_message.text(result.message);\n\n  if (result.status === \"authentication_required\") {\n    window.location = _CTFd[\"default\"].config.urlRoot + \"/login?next=\" + _CTFd[\"default\"].config.urlRoot + window.location.pathname + window.location.hash;\n    return;\n  } else if (result.status === \"incorrect\") {\n    // Incorrect key\n    result_notification.addClass(\"alert alert-danger alert-dismissable text-center\");\n    result_notification.slideDown();\n    answer_input.removeClass(\"correct\");\n    answer_input.addClass(\"wrong\");\n    setTimeout(function () {\n      answer_input.removeClass(\"wrong\");\n    }, 3000);\n  } else if (result.status === \"correct\") {\n    // Challenge Solved\n    result_notification.addClass(\"alert alert-success alert-dismissable text-center\");\n    result_notification.slideDown();\n\n    if ((0, _jquery[\"default\"])(\".challenge-solves\").text().trim()) {\n      // Only try to increment solves if the text isn't hidden\n      (0, _jquery[\"default\"])(\".challenge-solves\").text(parseInt((0, _jquery[\"default\"])(\".challenge-solves\").text().split(\" \")[0]) + 1 + \" Solves\");\n    }\n\n    answer_input.val(\"\");\n    answer_input.removeClass(\"wrong\");\n    answer_input.addClass(\"correct\");\n  } else if (result.status === \"already_solved\") {\n    // Challenge already solved\n    result_notification.addClass(\"alert alert-info alert-dismissable text-center\");\n    result_notification.slideDown();\n    answer_input.addClass(\"correct\");\n  } else if (result.status === \"paused\") {\n    // CTF is paused\n    result_notification.addClass(\"alert alert-warning alert-dismissable text-center\");\n    result_notification.slideDown();\n  } else if (result.status === \"ratelimited\") {\n    // Keys per minute too high\n    result_notification.addClass(\"alert alert-warning alert-dismissable text-center\");\n    result_notification.slideDown();\n    answer_input.addClass(\"too-fast\");\n    setTimeout(function () {\n      answer_input.removeClass(\"too-fast\");\n    }, 3000);\n  }\n\n  setTimeout(function () {\n    (0, _jquery[\"default\"])(\".alert\").slideUp();\n    (0, _jquery[\"default\"])(\"#challenge-submit\").removeClass(\"disabled-button\");\n    (0, _jquery[\"default\"])(\"#challenge-submit\").prop(\"disabled\", false);\n  }, 3000);\n}\n\nfunction markSolves() {\n  return _CTFd[\"default\"].api.get_user_solves({\n    userId: \"me\"\n  }).then(function (response) {\n    var solves = response.data;\n\n    for (var i = solves.length - 1; i >= 0; i--) {\n      var btn = (0, _jquery[\"default\"])('button[value=\"' + solves[i].challenge_id + '\"]');\n      btn.addClass(\"solved-challenge\");\n      btn.prepend(\"<i class='fas fa-check corner-button-check'></i>\");\n    }\n  });\n}\n\nfunction loadUserSolves() {\n  if (_CTFd[\"default\"].user.id == 0) {\n    return Promise.resolve();\n  }\n\n  return _CTFd[\"default\"].api.get_user_solves({\n    userId: \"me\"\n  }).then(function (response) {\n    solves = response.data;\n\n    for (var i = solves.length - 1; i >= 0; i--) {\n      var chal_id = solves[i].challenge_id;\n      solves.push(chal_id);\n    }\n  });\n}\n\nfunction getSolves(id) {\n  return _CTFd[\"default\"].api.get_challenge_solves({\n    challengeId: id\n  }).then(function (response) {\n    var data = response.data;\n    (0, _jquery[\"default\"])(\".challenge-solves\").text(parseInt(data.length) + \" Solves\");\n    var box = (0, _jquery[\"default\"])(\"#challenge-solves-names\");\n    box.empty();\n\n    for (var i = 0; i < data.length; i++) {\n      var _id = data[i].account_id;\n      var name = data[i].name;\n      var date = (0, _moment[\"default\"])(data[i].date).local().fromNow();\n      var account_url = data[i].account_url;\n      box.append('<tr><td><a href=\"{0}\">{2}</td><td>{3}</td></tr>'.format(account_url, _id, (0, _utils.htmlEntities)(name), date));\n    }\n  });\n}\n\n(0, _jquery[\"default\"])('select').on('change', function () {\n  loadChals();\n});\n\nfunction loadChals() {\n  return _loadChals.apply(this, arguments);\n}\n\nfunction _loadChals() {\n  _loadChals = _asyncToGenerator( /*#__PURE__*/_regeneratorRuntime[\"default\"].mark(function _callee2() {\n    return _regeneratorRuntime[\"default\"].wrap(function _callee2$(_context2) {\n      while (1) {\n        switch (_context2.prev = _context2.next) {\n          case 0:\n            //Add loading spinner while fetching API\n            (0, _jquery[\"default\"])(\"#challenges-board\").empty();\n            (0, _jquery[\"default\"])(\"#challenges-board\").append((0, _jquery[\"default\"])(\"\" + '<div class=\"min-vh-50 d-flex align-items-center\">' + '<div class=\"text-center w-100\">' + '<i class=\"fas fa-circle-notch fa-spin fa-3x fa-fw spinner\"></i>' + '</div>' + '</div>'));\n\n            if (!(challenges.length === 0)) {\n              _context2.next = 6;\n              break;\n            }\n\n            _context2.next = 5;\n            return _CTFd[\"default\"].api.get_challenge_list();\n\n          case 5:\n            challenges = _context2.sent.data;\n\n          case 6:\n            if (!(tagList.length === 0)) {\n              _context2.next = 10;\n              break;\n            }\n\n            _context2.next = 9;\n            return _CTFd[\"default\"].api.get_tag_list();\n\n          case 9:\n            tagList = _context2.sent.data;\n\n          case 10:\n            loadUserSolves().then( /*#__PURE__*/_asyncToGenerator( /*#__PURE__*/_regeneratorRuntime[\"default\"].mark(function _callee() {\n              var challengesBoard, orderValue, i, ID, tagrow, _i, j, chalinfo, chalid, tagID, chalwrap, _chalbutton, chalheader, _j, tag, _i2, _chalinfo, chalrow, _chalrow, _chalrow2, _i3, _chalinfo2, _chalid, classValue, _chalwrap, _chalbutton2, _chalheader, authorList, _i4, _chalwrap2, user, _chalrow3, chalbutton, _chalheader2;\n\n              return _regeneratorRuntime[\"default\"].wrap(function _callee$(_context) {\n                while (1) {\n                  switch (_context.prev = _context.next) {\n                    case 0:\n                      challengesBoard = (0, _jquery[\"default\"])(\"<div></div>\");\n                      orderValue = (0, _jquery[\"default\"])(\"#challenges_filter option:selected\").val(); //Set up default tag/challenge values.\n\n                      if (!(orderValue === undefined)) {\n                        _context.next = 6;\n                        break;\n                      }\n\n                      orderValue = \"tag\";\n                      _context.next = 48;\n                      break;\n\n                    case 6:\n                      if (!(orderValue === \"tag\")) {\n                        _context.next = 13;\n                        break;\n                      }\n\n                      tagList.sort(function (a, b) {\n                        return a.value.localeCompare(b.value);\n                      });\n                      tagList.reverse();\n\n                      for (i = tagList.length - 1; i >= 0; i--) {\n                        //for (let i = 0; i <=tagList.length ; i++) {\n                        ID = tagList[i].value.replace(/ /g, \"-\").hashCode();\n                        tagrow = (0, _jquery[\"default\"])(\"\" + '<div id=\"{0}-row\" class=\"pt-5\">'.format(ID) + '<div class=\"tag-header col-md-12 mb-3\">' + \"</div>\" + '<div class=\"tag-challenge col-md-12\">' + '<div class=\"challenges-row col-md-12\"></div>' + \"</div>\" + \"</div>\");\n                        tagrow.find(\".tag-header\").append((0, _jquery[\"default\"])(\"<h3>\" + tagList[i].value + \"</h3>\"));\n                        challengesBoard.append(tagrow);\n                      }\n\n                      for (_i = 0; _i < challenges.length; _i++) {\n                        for (j = 0; j < challenges[_i].tags.length; j++) {\n                          chalinfo = challenges[_i];\n                          chalid = chalinfo.name.replace(/ /g, \"-\").hashCode();\n                          tagID = challenges[_i].tags[j].value.replace(/ /g, \"-\").hashCode();\n                          chalwrap = (0, _jquery[\"default\"])(\"<div id='{0}' class='col-md-3 d-inline-block'></div>\".format(chalid));\n                          _chalbutton = void 0;\n\n                          if (solves.indexOf(chalinfo.id) == -1) {\n                            _chalbutton = (0, _jquery[\"default\"])(\"<button class='btn btn-dark challenge-button w-100 text-truncate pt-3 pb-3 mb-2' value='{0}'></button>\".format(chalinfo.id));\n                          } else {\n                            _chalbutton = (0, _jquery[\"default\"])(\"<button class='btn btn-dark challenge-button solved-challenge w-100 text-truncate pt-3 pb-3 mb-2' value='{0}'><i class='fas fa-check corner-button-check'></i></button>\".format(chalinfo.id));\n                          }\n\n                          chalheader = (0, _jquery[\"default\"])(\"<p>{0}</p>\".format(chalinfo.name));\n\n                          for (_j = 0; _j < chalinfo.tags.length; _j++) {\n                            tag = \"tag-\" + chalinfo.tags[_j].value.replace(/ /g, \"-\");\n                            chalwrap.addClass(tag);\n                          }\n\n                          _chalbutton.append(chalheader);\n\n                          chalwrap.append(_chalbutton);\n                          challengesBoard.find(\"#\" + tagID + \"-row > .tag-challenge > .challenges-row\").append(chalwrap);\n                        }\n                      }\n\n                      _context.next = 48;\n                      break;\n\n                    case 13:\n                      if (!(orderValue == \"name\")) {\n                        _context.next = 19;\n                        break;\n                      }\n\n                      challenges.sort(function (a, b) {\n                        return a.name.localeCompare(b.name);\n                      });\n                      challenges.reverse();\n\n                      for (_i2 = challenges.length - 1; _i2 >= 0; _i2--) {\n                        _chalinfo = challenges[_i2];\n\n                        if (solves.indexOf(_chalinfo.id) == -1) {\n                          chalrow = (0, _jquery[\"default\"])(\"\" + '<button class=\"btn btn-dark challenge-button w-100 text-truncate col-md-3\" style=\"margin-right:1rem; margin-top:2rem\" value=\"{0}\"></button>'.format(_chalinfo.id) + \"</div>\");\n                          chalrow.append((0, _jquery[\"default\"])(\"<h3>\" + challenges[_i2].name + \"</h3>\"));\n                          challengesBoard.append(chalrow);\n                        } else if (solves.indexOf(_chalinfo.id) !== -1) {\n                          _chalrow = (0, _jquery[\"default\"])(\"\" + '<button class=\"btn btn-dark challenge-button w-100 solved-challenge text-truncate col-md-3\" style=\"margin-right:1rem; margin-top:2rem\" value=\"{0}\"></button>'.format(_chalinfo.id));\n\n                          _chalrow.append((0, _jquery[\"default\"])(\"<h3>\" + challenges[_i2].name + \"</h3>\"));\n\n                          challengesBoard.append(_chalrow);\n                        }\n                      }\n\n                      _context.next = 48;\n                      break;\n\n                    case 19:\n                      if (!(orderValue == \"solved\")) {\n                        _context.next = 27;\n                        break;\n                      }\n\n                      challenges.sort(function (a, b) {\n                        return a.name.localeCompare(b.name);\n                      });\n                      challenges.reverse();\n                      _chalrow2 = (0, _jquery[\"default\"])(\"\" + '<div class=\"solved-header col-md-12 mb-3\">' + \"<h3> Solved </h3>\" + '<div class=\"challenges-row col-md-12\"></div>' + \"</div>\" + '<div class=\"unsolved-header col-md-12 mb-3\">' + \"<h3> Unsolved </h3>\" + '<div class=\"challenges-row col-md-12\"></div>' + \"</div>\");\n                      challengesBoard.append(_chalrow2);\n\n                      for (_i3 = challenges.length - 1; _i3 >= 0; _i3--) {\n                        _chalinfo2 = challenges[_i3];\n                        _chalid = _chalinfo2.name.replace(/ /g, \"-\").hashCode();\n                        classValue = void 0;\n                        _chalwrap = (0, _jquery[\"default\"])(\"<div id='{0}' class='col-md-3 d-inline-block'></div>\".format(_chalid));\n                        _chalbutton2 = void 0;\n\n                        if (solves.indexOf(_chalinfo2.id) == -1) {\n                          _chalbutton2 = (0, _jquery[\"default\"])(\"<button class='btn btn-dark challenge-button w-100 text-truncate pt-3 pb-3 mb-2' value='{0}'></button>\".format(_chalinfo2.id));\n                          classValue = \".unsolved-header\";\n                        } else {\n                          _chalbutton2 = (0, _jquery[\"default\"])(\"<button class='btn btn-dark challenge-button solved-challenge w-100 text-truncate pt-3 pb-3 mb-2' value='{0}'><i class='fas fa-check corner-button-check'></i></button>\".format(_chalinfo2.id));\n                          classValue = \".solved-header\";\n                        }\n\n                        _chalheader = (0, _jquery[\"default\"])(\"<p>{0}</p>\".format(_chalinfo2.name));\n\n                        _chalbutton2.append(_chalheader);\n\n                        _chalwrap.append(_chalbutton2);\n\n                        challengesBoard.find(classValue + \" > .challenges-row\").append(_chalwrap);\n                      }\n\n                      _context.next = 48;\n                      break;\n\n                    case 27:\n                      if (!(orderValue === \"author\")) {\n                        _context.next = 48;\n                        break;\n                      }\n\n                      authorList = [];\n                      _i4 = 0;\n\n                    case 30:\n                      if (!(_i4 < challenges.length)) {\n                        _context.next = 48;\n                        break;\n                      }\n\n                      _chalwrap2 = (0, _jquery[\"default\"])(\"<div id='{0}' class='col-md-3 d-inline-block'></div>\".format(challenges[_i4].id));\n\n                      if (!(authorList.indexOf(challenges[_i4].authorId) === -1)) {\n                        _context.next = 40;\n                        break;\n                      }\n\n                      authorList.push(challenges[_i4].authorId);\n                      _context.next = 36;\n                      return _CTFd[\"default\"].api.get_user_public({\n                        userId: challenges[_i4].authorId\n                      });\n\n                    case 36:\n                      user = _context.sent.data;\n                      _chalrow3 = (0, _jquery[\"default\"])(\"\" + '<div id=\"{0}-row\" class=\"pt-5\">'.format(challenges[_i4].authorId) + '<div class=\"author-header col-md-12 mb-3\">' + \"</div>\" + '<div class=\"author-challenge col-md-12\">' + '<div class=\"challenges-row col-md-12\"></div>' + \"</div>\" + \"</div>\");\n\n                      _chalrow3.find(\".author-header\").append((0, _jquery[\"default\"])(\"<h3>\" + user.name + \"</h3>\"));\n\n                      challengesBoard.append(_chalrow3);\n\n                    case 40:\n                      if (solves.indexOf(challenges[_i4].id) === -1) {\n                        chalbutton = (0, _jquery[\"default\"])(\"<button class='btn btn-dark challenge-button w-100 text-truncate pt-3 pb-3 mb-2' value='{0}'></button>\".format(challenges[_i4].id));\n                      } else {\n                        chalbutton = (0, _jquery[\"default\"])(\"<button class='btn btn-dark challenge-button solved-challenge w-100 text-truncate pt-3 pb-3 mb-2' value='{0}'><i class='fas fa-check corner-button-check'></i></button>\".format(challenges[_i4].id));\n                      }\n\n                      _chalheader2 = (0, _jquery[\"default\"])(\"<p>{0}</p>\".format(challenges[_i4].name));\n                      chalbutton.append(_chalheader2);\n\n                      _chalwrap2.append(chalbutton);\n\n                      challengesBoard.find(\"#\" + challenges[_i4].authorId + \"-row > .author-challenge > .challenges-row\").append(_chalwrap2);\n\n                    case 45:\n                      _i4++;\n                      _context.next = 30;\n                      break;\n\n                    case 48:\n                      (0, _jquery[\"default\"])(\"#challenges-board\").empty();\n                      (0, _jquery[\"default\"])(\"#challenges-board\").append(challengesBoard);\n                      (0, _jquery[\"default\"])(\".challenge-button\").click(function (_event) {\n                        loadChal(this.value);\n                        getSolves(this.value);\n                      });\n\n                    case 51:\n                    case \"end\":\n                      return _context.stop();\n                  }\n                }\n              }, _callee);\n            })));\n\n          case 11:\n          case \"end\":\n            return _context2.stop();\n        }\n      }\n    }, _callee2);\n  }));\n  return _loadChals.apply(this, arguments);\n}\n\nfunction update() {\n  return loadUserSolves() // Load the user's solved challenge ids\n  .then(loadChals) //  Load the full list of challenges\n  .then(markSolves);\n}\n\n(0, _jquery[\"default\"])(function () {\n  update().then(function () {\n    if (window.location.hash.length > 0) {\n      loadChalByName(decodeURIComponent(window.location.hash.substring(1)));\n    }\n  });\n  (0, _jquery[\"default\"])(\"#challenge-input\").keyup(function (event) {\n    if (event.keyCode == 13) {\n      (0, _jquery[\"default\"])(\"#challenge-submit\").click();\n    }\n  });\n  (0, _jquery[\"default\"])(\".nav-tabs a\").click(function (event) {\n    event.preventDefault();\n    (0, _jquery[\"default\"])(this).tab(\"show\");\n  });\n  (0, _jquery[\"default\"])(\"#challenge-window\").on(\"hidden.bs.modal\", function (_event) {\n    (0, _jquery[\"default\"])(\".nav-tabs a:first\").tab(\"show\");\n    history.replaceState(\"\", window.document.title, window.location.pathname);\n  });\n  (0, _jquery[\"default\"])(\".challenge-solves\").click(function (_event) {\n    getSolves((0, _jquery[\"default\"])(\"#challenge-id\").val());\n  });\n  (0, _jquery[\"default\"])(\"#challenge-window\").on(\"hide.bs.modal\", function (_event) {\n    (0, _jquery[\"default\"])(\"#challenge-input\").removeClass(\"wrong\");\n    (0, _jquery[\"default\"])(\"#challenge-input\").removeClass(\"correct\");\n    (0, _jquery[\"default\"])(\"#incorrect-key\").slideUp();\n    (0, _jquery[\"default\"])(\"#correct-key\").slideUp();\n    (0, _jquery[\"default\"])(\"#already-solved\").slideUp();\n    (0, _jquery[\"default\"])(\"#too-fast\").slideUp();\n  });\n});\nsetInterval(update, 300000); // Update every 5 minutes.\n\nvar displayHint = function displayHint(data) {\n  (0, _ezq.ezAlert)({\n    title: \"Hint\",\n    body: data.html,\n    button: \"Got it!\"\n  });\n};\n\nvar displayUnlock = function displayUnlock(id) {\n  (0, _ezq.ezQuery)({\n    title: \"Unlock Hint?\",\n    body: \"Are you sure you want to open this hint?\",\n    success: function success() {\n      var params = {\n        target: id,\n        type: \"hints\"\n      };\n\n      _CTFd[\"default\"].api.post_unlock_list({}, params).then(function (response) {\n        if (response.success) {\n          _CTFd[\"default\"].api.get_hint({\n            hintId: id\n          }).then(function (response) {\n            displayHint(response.data);\n          });\n\n          return;\n        }\n\n        (0, _ezq.ezAlert)({\n          title: \"Error\",\n          body: \"\",\n          button: \"Got it!\"\n        });\n      });\n    }\n  });\n};\n\nvar loadHint = function loadHint(id) {\n  _CTFd[\"default\"].api.get_hint({\n    hintId: id\n  }).then(function (response) {\n    if (response.data.content) {\n      displayHint(response.data);\n      return;\n    }\n\n    displayUnlock(id);\n  });\n};\n\n//# sourceURL=webpack:///./CTFd/themes/core/assets/js/pages/challenges.js?");

/***/ })

/******/ });