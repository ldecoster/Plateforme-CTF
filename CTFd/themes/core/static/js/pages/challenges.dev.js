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
eval("\n\n__webpack_require__(/*! ./main */ \"./CTFd/themes/core/assets/js/pages/main.js\");\n\n__webpack_require__(/*! bootstrap/js/dist/tab */ \"./node_modules/bootstrap/js/dist/tab.js\");\n\nvar _ezq = __webpack_require__(/*! ../ezq */ \"./CTFd/themes/core/assets/js/ezq.js\");\n\nvar _utils = __webpack_require__(/*! ../utils */ \"./CTFd/themes/core/assets/js/utils.js\");\n\nvar _dayjs = _interopRequireDefault(__webpack_require__(/*! dayjs */ \"./node_modules/dayjs/dayjs.min.js\"));\n\nvar _relativeTime = _interopRequireDefault(__webpack_require__(/*! dayjs/plugin/relativeTime */ \"./node_modules/dayjs/plugin/relativeTime.js\"));\n\nvar _jquery = _interopRequireDefault(__webpack_require__(/*! jquery */ \"./node_modules/jquery/dist/jquery.js\"));\n\nvar _CTFd = _interopRequireDefault(__webpack_require__(/*! ../CTFd */ \"./CTFd/themes/core/assets/js/CTFd.js\"));\n\nvar _config = _interopRequireDefault(__webpack_require__(/*! ../config */ \"./CTFd/themes/core/assets/js/config.js\"));\n\nvar _highlight = _interopRequireDefault(__webpack_require__(/*! highlight.js */ \"./node_modules/highlight.js/lib/index.js\"));\n\nfunction _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { \"default\": obj }; }\n\nfunction _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }\n\nfunction _toConsumableArray(arr) { return _arrayWithoutHoles(arr) || _iterableToArray(arr) || _unsupportedIterableToArray(arr) || _nonIterableSpread(); }\n\nfunction _nonIterableSpread() { throw new TypeError(\"Invalid attempt to spread non-iterable instance.\\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.\"); }\n\nfunction _iterableToArray(iter) { if (typeof Symbol !== \"undefined\" && Symbol.iterator in Object(iter)) return Array.from(iter); }\n\nfunction _arrayWithoutHoles(arr) { if (Array.isArray(arr)) return _arrayLikeToArray(arr); }\n\nfunction _createForOfIteratorHelper(o, allowArrayLike) { var it; if (typeof Symbol === \"undefined\" || o[Symbol.iterator] == null) { if (Array.isArray(o) || (it = _unsupportedIterableToArray(o)) || allowArrayLike && o && typeof o.length === \"number\") { if (it) o = it; var i = 0; var F = function F() {}; return { s: F, n: function n() { if (i >= o.length) return { done: true }; return { done: false, value: o[i++] }; }, e: function e(_e) { throw _e; }, f: F }; } throw new TypeError(\"Invalid attempt to iterate non-iterable instance.\\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.\"); } var normalCompletion = true, didErr = false, err; return { s: function s() { it = o[Symbol.iterator](); }, n: function n() { var step = it.next(); normalCompletion = step.done; return step; }, e: function e(_e2) { didErr = true; err = _e2; }, f: function f() { try { if (!normalCompletion && it[\"return\"] != null) it[\"return\"](); } finally { if (didErr) throw err; } } }; }\n\nfunction _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === \"string\") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === \"Object\" && o.constructor) n = o.constructor.name; if (n === \"Map\" || n === \"Set\") return Array.from(o); if (n === \"Arguments\" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }\n\nfunction _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }\n\n_dayjs[\"default\"].extend(_relativeTime[\"default\"]);\n\n_CTFd[\"default\"]._internal.challenge = {};\nvar challenges = [];\nvar solves = [];\nvar tag_list = [];\nvar $challenges_board = (0, _jquery[\"default\"])(\"#challenges-board\");\nvar $spinner_content = $challenges_board.children().detach();\n\nvar loadChal = function loadChal(id) {\n  var chal = _jquery[\"default\"].grep(challenges, function (chal) {\n    return chal.id == id;\n  })[0];\n\n  if (chal.state === \"hidden\") {\n    (0, _ezq.ezAlert)({\n      title: \"Challenge Hidden!\",\n      body: \"You haven't unlocked this challenge yet!\",\n      button: \"Got it!\"\n    });\n    return;\n  }\n\n  displayChal(chal);\n};\n\nvar loadChalByName = function loadChalByName(name) {\n  var idx = name.lastIndexOf(\"-\");\n  var pieces = [name.slice(0, idx), name.slice(idx + 1)];\n  var id = pieces[1];\n\n  var chal = _jquery[\"default\"].grep(challenges, function (chal) {\n    return chal.id == id;\n  })[0];\n\n  displayChal(chal);\n};\n\nvar displayChal = function displayChal(chal) {\n  return Promise.all([_CTFd[\"default\"].api.get_challenge({\n    challengeId: chal.id\n  }), _jquery[\"default\"].getScript(_config[\"default\"].urlRoot + chal.script), _jquery[\"default\"].get(_config[\"default\"].urlRoot + chal.template)]).then(function (responses) {\n    var challenge = _CTFd[\"default\"]._internal.challenge;\n    (0, _jquery[\"default\"])(\"#challenge-window\").empty(); // Inject challenge data into the plugin\n\n    challenge.data = responses[0].data; // Call preRender function in plugin\n\n    challenge.preRender(); // Build HTML from the Jinja response in API\n\n    (0, _jquery[\"default\"])(\"#challenge-window\").append(responses[0].data.view);\n    (0, _jquery[\"default\"])(\"#challenge-window #challenge-input\").addClass(\"form-control\");\n    (0, _jquery[\"default\"])(\"#challenge-window #challenge-submit\").addClass(\"btn btn-md btn-outline-secondary float-right\");\n    var modal = (0, _jquery[\"default\"])(\"#challenge-window\").find(\".modal-dialog\");\n\n    if (window.init.theme_settings && window.init.theme_settings.challenge_window_size) {\n      switch (window.init.theme_settings.challenge_window_size) {\n        case \"sm\":\n          modal.addClass(\"modal-sm\");\n          break;\n\n        case \"lg\":\n          modal.addClass(\"modal-lg\");\n          break;\n\n        case \"xl\":\n          modal.addClass(\"modal-xl\");\n          break;\n\n        default:\n          break;\n      }\n    }\n\n    (0, _jquery[\"default\"])(\".challenge-solves\").click(function (_event) {\n      getSolves((0, _jquery[\"default\"])(\"#challenge-id\").val());\n    });\n    (0, _jquery[\"default\"])(\".nav-tabs a\").click(function (event) {\n      event.preventDefault();\n      (0, _jquery[\"default\"])(this).tab(\"show\");\n    }); // Handle modal toggling\n\n    (0, _jquery[\"default\"])(\"#challenge-window\").on(\"hide.bs.modal\", function (_event) {\n      (0, _jquery[\"default\"])(\"#challenge-input\").removeClass(\"wrong\");\n      (0, _jquery[\"default\"])(\"#challenge-input\").removeClass(\"correct\");\n      (0, _jquery[\"default\"])(\"#incorrect-key\").slideUp();\n      (0, _jquery[\"default\"])(\"#correct-key\").slideUp();\n      (0, _jquery[\"default\"])(\"#already-solved\").slideUp();\n      (0, _jquery[\"default\"])(\"#too-fast\").slideUp();\n    });\n    (0, _jquery[\"default\"])(\".load-ressource\").on(\"click\", function (_event) {\n      loadRessource((0, _jquery[\"default\"])(this).data(\"ressource-id\"));\n    });\n    (0, _jquery[\"default\"])(\"#challenge-submit\").click(function (event) {\n      event.preventDefault();\n      (0, _jquery[\"default\"])(\"#challenge-submit\").addClass(\"disabled-button\");\n      (0, _jquery[\"default\"])(\"#challenge-submit\").prop(\"disabled\", true);\n\n      _CTFd[\"default\"]._internal.challenge.submit().then(renderSubmissionResponse).then(loadChals).then(markSolves);\n    });\n    (0, _jquery[\"default\"])(\"#challenge-input\").keyup(function (event) {\n      if (event.keyCode == 13) {\n        (0, _jquery[\"default\"])(\"#challenge-submit\").click();\n      }\n    });\n    challenge.postRender();\n    (0, _jquery[\"default\"])(\"#challenge-window\").find(\"pre code\").each(function (_idx) {\n      _highlight[\"default\"].highlightBlock(this);\n    });\n    window.location.replace(window.location.href.split(\"#\")[0] + \"#\".concat(chal.name, \"-\").concat(chal.id));\n    (0, _jquery[\"default\"])(\"#challenge-window\").modal();\n  });\n};\n\nfunction renderSubmissionResponse(response) {\n  var result = response.data;\n  var result_message = (0, _jquery[\"default\"])(\"#result-message\");\n  var result_notification = (0, _jquery[\"default\"])(\"#result-notification\");\n  var answer_input = (0, _jquery[\"default\"])(\"#challenge-input\");\n  result_notification.removeClass();\n  result_message.text(result.message);\n\n  if (result.status === \"authentication_required\") {\n    window.location = _CTFd[\"default\"].config.urlRoot + \"/login?next=\" + _CTFd[\"default\"].config.urlRoot + window.location.pathname + window.location.hash;\n    return;\n  } else if (result.status === \"incorrect\") {\n    // Incorrect key\n    result_notification.addClass(\"alert alert-danger alert-dismissable text-center\");\n    result_notification.slideDown();\n    answer_input.removeClass(\"correct\");\n    answer_input.addClass(\"wrong\");\n    setTimeout(function () {\n      answer_input.removeClass(\"wrong\");\n    }, 3000);\n  } else if (result.status === \"correct\") {\n    // Challenge Solved\n    result_notification.addClass(\"alert alert-success alert-dismissable text-center\");\n    result_notification.slideDown(); // We clear the challenge list to force a reload and get the unlocked chals\n\n    challenges = [];\n\n    if ((0, _jquery[\"default\"])(\".challenge-solves\").text().trim()) {\n      // Only try to increment solves if the text isn't hidden\n      (0, _jquery[\"default\"])(\".challenge-solves\").text(parseInt((0, _jquery[\"default\"])(\".challenge-solves\").text().split(\" \")[0]) + 1 + \" Solves\");\n    }\n\n    answer_input.val(\"\");\n    answer_input.removeClass(\"wrong\");\n    answer_input.addClass(\"correct\");\n  } else if (result.status === \"already_solved\") {\n    // Challenge already solved\n    result_notification.addClass(\"alert alert-info alert-dismissable text-center\");\n    result_notification.slideDown();\n    answer_input.addClass(\"correct\");\n  } else if (result.status === \"paused\") {\n    // CTF is paused\n    result_notification.addClass(\"alert alert-warning alert-dismissable text-center\");\n    result_notification.slideDown();\n  } else if (result.status === \"ratelimited\") {\n    // Keys per minute too high\n    result_notification.addClass(\"alert alert-warning alert-dismissable text-center\");\n    result_notification.slideDown();\n    answer_input.addClass(\"too-fast\");\n    setTimeout(function () {\n      answer_input.removeClass(\"too-fast\");\n    }, 3000);\n  }\n\n  setTimeout(function () {\n    (0, _jquery[\"default\"])(\".alert\").slideUp();\n    (0, _jquery[\"default\"])(\"#challenge-submit\").removeClass(\"disabled-button\");\n    (0, _jquery[\"default\"])(\"#challenge-submit\").prop(\"disabled\", false);\n  }, 3000);\n}\n\nfunction markSolves() {\n  challenges.map(function (challenge) {\n    if (challenge.solved_by_me) {\n      var btn = (0, _jquery[\"default\"])(\"button[value=\\\"\".concat(challenge.id, \"\\\"]\"));\n      btn.addClass(\"solved-challenge\");\n      btn.prepend(\"<i class='fas fa-check corner-button-check'></i>\");\n    }\n  });\n}\n\nfunction getSolves(id) {\n  return _CTFd[\"default\"].api.get_challenge_solves({\n    challengeId: id\n  }).then(function (response) {\n    var data = response.data;\n    (0, _jquery[\"default\"])(\".challenge-solves\").text(parseInt(data.length) + \" Solves\");\n    var box = (0, _jquery[\"default\"])(\"#challenge-solves-names\");\n    box.empty();\n\n    for (var i = 0; i < data.length; i++) {\n      var _id = data[i].account_id;\n      var name = data[i].name;\n      var date = (0, _dayjs[\"default\"])(data[i].date).fromNow();\n      var account_url = data[i].account_url;\n      box.append('<tr><td><a href=\"{0}\">{2}</td><td>{3}</td></tr>'.format(account_url, _id, (0, _utils.htmlEntities)(name), date));\n    }\n  });\n}\n\n(0, _jquery[\"default\"])('select').on('change', function () {\n  update();\n});\n\nfunction createChalWrapper(chalinfo, catid) {\n  var chalid = catid + '_' + chalinfo.name.replace(/ /g, \"-\").hashCode();\n  var chalwrap = (0, _jquery[\"default\"])(\"<div id='{0}' class='col-md-3 d-inline-block'></div>\".format(chalid));\n  var chalbutton;\n\n  if (solves.indexOf(chalinfo.id) === -1) {\n    chalbutton = (0, _jquery[\"default\"])(\"<button class='btn btn-dark challenge-button w-100 text-truncate pt-3 pb-3 mb-2' value='{0}'></button>\".format(chalinfo.id));\n  } else {\n    chalbutton = (0, _jquery[\"default\"])(\"<button class='btn btn-dark challenge-button solved-challenge w-100 text-truncate pt-3 pb-3 mb-2' value='{0}'><i class='fas fa-check corner-button-check'></i></button>\".format(chalinfo.id));\n  }\n\n  var chalheader = (0, _jquery[\"default\"])(\"<p>{0}</p>\".format(chalinfo.name));\n  chalbutton.append(chalheader);\n  chalwrap.append(chalbutton);\n  (0, _jquery[\"default\"])(\"#\" + catid + \"-row\").find(\".category-challenges > .challenges-row\").append(chalwrap);\n}\n\nfunction loadChals() {\n  return _CTFd[\"default\"].api.get_challenge_list().then(function (response) {\n    var categories = [];\n    var challenges_filter = (0, _jquery[\"default\"])(\"#challenges_filter option:selected\").val();\n    challenges = response.data;\n\n    switch (challenges_filter) {\n      case \"author\":\n        {\n          $challenges_board.empty();\n\n          for (var i = challenges.length - 1; i >= 0; i--) {\n            if (_jquery[\"default\"].inArray(challenges[i].author_name, categories) === -1) {\n              var category = challenges[i].author_name;\n              categories.push(category);\n              var categoryid = category.replace(/ /g, \"-\").hashCode();\n              var categoryrow = (0, _jquery[\"default\"])(\"\" + '<div id=\"{0}-row\" class=\"pt-5\">'.format(categoryid) + '<div class=\"category-header col-md-12 mb-3\">' + \"</div>\" + '<div class=\"category-challenges col-md-12\">' + '<div class=\"challenges-row col-md-12\"></div>' + \"</div>\" + \"</div>\");\n              categoryrow.find(\".category-header\").append((0, _jquery[\"default\"])(\"<h3>\" + category + \"</h3>\"));\n              $challenges_board.append(categoryrow);\n            }\n          }\n\n          for (var _i = 0; _i <= challenges.length - 1; _i++) {\n            var chalinfo = challenges[_i];\n\n            var catid = challenges[_i].author_name.replace(/ /g, \"-\").hashCode();\n\n            createChalWrapper(chalinfo, catid);\n          }\n\n          break;\n        }\n\n      case \"solved\":\n        {\n          $challenges_board.empty();\n          categories.push(\"Unsolved\", \"Solved\");\n\n          var _iterator = _createForOfIteratorHelper(categories),\n              _step;\n\n          try {\n            for (_iterator.s(); !(_step = _iterator.n()).done;) {\n              var _category = _step.value;\n\n              var _categoryid = _category.replace(/ /g, \"-\").hashCode();\n\n              var _categoryrow = (0, _jquery[\"default\"])(\"\" + '<div id=\"{0}-row\" class=\"pt-5\">'.format(_categoryid) + '<div class=\"category-header col-md-12 mb-3\">' + \"</div>\" + '<div class=\"category-challenges col-md-12\">' + '<div class=\"challenges-row col-md-12\"></div>' + \"</div>\" + \"</div>\");\n\n              _categoryrow.find(\".category-header\").append((0, _jquery[\"default\"])(\"<h3>\" + _category + \"</h3>\"));\n\n              $challenges_board.append(_categoryrow);\n            }\n          } catch (err) {\n            _iterator.e(err);\n          } finally {\n            _iterator.f();\n          }\n\n          for (var _i2 = 0; _i2 <= challenges.length - 1; _i2++) {\n            var _chalinfo = challenges[_i2];\n\n            var _catid = challenges[_i2].solved_by_me ? \"Solved\".replace(/ /g, \"-\").hashCode() : \"Unsolved\".replace(/ /g, \"-\").hashCode();\n\n            createChalWrapper(_chalinfo, _catid);\n          }\n\n          break;\n        }\n\n      case \"name\":\n        {\n          var _categoryid2 = \"names\".replace(/ /g, \"-\").hashCode();\n\n          var _categoryrow2 = (0, _jquery[\"default\"])(\"\" + '<div id=\"{0}-row\" class=\"pt-5\">'.format(_categoryid2) + '<div class=\"category-header col-md-12 mb-3\">' + \"</div>\" + '<div class=\"category-challenges col-md-12\">' + '<div class=\"challenges-row col-md-12\"></div>' + \"</div>\" + \"</div>\");\n\n          $challenges_board.empty();\n          $challenges_board.append(_categoryrow2);\n          challenges.sort(function (a, b) {\n            return a.name.localeCompare(b.name);\n          });\n\n          for (var _i3 = 0; _i3 <= challenges.length - 1; _i3++) {\n            var _chalinfo2 = challenges[_i3];\n            createChalWrapper(_chalinfo2, _categoryid2);\n          }\n\n          break;\n        }\n\n      case \"exercise\":\n        {\n          return _CTFd[\"default\"].api.get_tag_list().then(function (tagResponse) {\n            return _CTFd[\"default\"].api.get_badge_list().then(function (badgeResponse) {\n              return _CTFd[\"default\"].api.get_user_badges().then(function (userBadgesRes) {\n                tag_list = tagResponse.data;\n                tag_list.sort(function (a, b) {\n                  return b.value.localeCompare(a.value);\n                });\n                var badge_list = Object.assign.apply(Object, [{}].concat(_toConsumableArray(badgeResponse.data.map(function (badge) {\n                  return _defineProperty({}, badge.tag_id, badge.name);\n                }))));\n                var user_badges = Object.assign.apply(Object, [{}].concat(_toConsumableArray(userBadgesRes.data.map(function (badge) {\n                  return _defineProperty({}, badge.tag_id, badge.name);\n                }))));\n                $challenges_board.empty();\n\n                for (var _i4 = tag_list.length - 1; _i4 >= 0; _i4--) {\n                  if (_jquery[\"default\"].inArray(tag_list[_i4].value, categories) === -1 && tag_list[_i4].exercise) {\n                    var _category2 = tag_list[_i4].value;\n                    categories.push(_category2);\n\n                    var _categoryid3 = _category2.replace(/ /g, \"-\").hashCode();\n\n                    var _categoryrow3 = (0, _jquery[\"default\"])(\"\" + '<div id=\"{0}-row\" class=\"pt-5\">'.format(_categoryid3) + '<div class=\"category-header col-md-12 mb-3\"' + 'style=\"display: flex; align-items: center;' + '\">' + \"</div>\" + '<div class=\"category-challenges col-md-12\">' + '<div class=\"challenges-row col-md-12\"></div>' + \"</div>\" + \"</div>\");\n\n                    _categoryrow3.find(\".category-header\").append((0, _jquery[\"default\"])(\"<h3 class='mb-0'>\" + _category2 + \"</h3>\"));\n\n                    if (badge_list[tag_list[_i4].id]) {\n                      _categoryrow3.find(\".category-header\").append((0, _jquery[\"default\"])(\"<div>\" + \"<span class='badge badge-pill {0} ml-2'>\".format(user_badges[tag_list[_i4].id] ? 'badge-success' : 'badge-secondary') + \"<span>{0}</span>\".format(badge_list[tag_list[_i4].id]) + \"</span>\" + \"</div>\"));\n                    }\n\n                    $challenges_board.append(_categoryrow3);\n                  }\n                }\n\n                for (var _i5 = 0; _i5 <= challenges.length - 1; _i5++) {\n                  for (var j = 0; j <= challenges[_i5].tags.length - 1; j++) {\n                    var _chalinfo3 = challenges[_i5];\n\n                    var _catid2 = challenges[_i5].tags[j].value.replace(/ /g, \"-\").hashCode();\n\n                    createChalWrapper(_chalinfo3, _catid2);\n                  }\n                }\n\n                (0, _jquery[\"default\"])(\".challenge-button\").click(function (_event) {\n                  loadChal(this.value);\n                });\n              });\n            });\n          });\n        }\n\n      case \"tag\":\n      default:\n        {\n          $challenges_board.empty();\n          return _CTFd[\"default\"].api.get_tag_list().then(function (response) {\n            tag_list = response.data;\n            tag_list.sort(function (a, b) {\n              return b.value.localeCompare(a.value);\n            });\n\n            for (var _i6 = tag_list.length - 1; _i6 >= 0; _i6--) {\n              if (_jquery[\"default\"].inArray(tag_list[_i6].value, categories) === -1 && !tag_list[_i6].exercise) {\n                var _category3 = tag_list[_i6].value;\n                categories.push(_category3);\n\n                var _categoryid4 = _category3.replace(/ /g, \"-\").hashCode();\n\n                var _categoryrow4 = (0, _jquery[\"default\"])(\"\" + '<div id=\"{0}-row\" class=\"pt-5\">'.format(_categoryid4) + '<div class=\"category-header col-md-12 mb-3\">' + \"</div>\" + '<div class=\"category-challenges col-md-12\">' + '<div class=\"challenges-row col-md-12\"></div>' + \"</div>\" + \"</div>\");\n\n                _categoryrow4.find(\".category-header\").append((0, _jquery[\"default\"])(\"<h3>\" + _category3 + \"</h3>\"));\n\n                $challenges_board.append(_categoryrow4);\n              }\n            }\n\n            for (var _i7 = 0; _i7 <= challenges.length - 1; _i7++) {\n              for (var j = 0; j <= challenges[_i7].tags.length - 1; j++) {\n                var _chalinfo4 = challenges[_i7];\n\n                var _catid3 = challenges[_i7].tags[j].value.replace(/ /g, \"-\").hashCode();\n\n                createChalWrapper(_chalinfo4, _catid3);\n              }\n            }\n\n            (0, _jquery[\"default\"])(\".challenge-button\").click(function (_event) {\n              loadChal(this.value);\n            });\n          });\n        }\n    }\n\n    (0, _jquery[\"default\"])(\".challenge-button\").click(function (_event) {\n      loadChal(this.value);\n    });\n  });\n}\n\nfunction update() {\n  $challenges_board.empty();\n  $challenges_board.append($spinner_content);\n  return loadChals().then(markSolves);\n}\n\n(0, _jquery[\"default\"])(function () {\n  update().then(function () {\n    if (window.location.hash.length > 0) {\n      loadChalByName(decodeURIComponent(window.location.hash.substring(1)));\n    }\n  });\n  (0, _jquery[\"default\"])(\"#challenge-input\").keyup(function (event) {\n    if (event.keyCode == 13) {\n      (0, _jquery[\"default\"])(\"#challenge-submit\").click();\n    }\n  });\n  (0, _jquery[\"default\"])(\".nav-tabs a\").click(function (event) {\n    event.preventDefault();\n    (0, _jquery[\"default\"])(this).tab(\"show\");\n  });\n  (0, _jquery[\"default\"])(\"#challenge-window\").on(\"hidden.bs.modal\", function (_event) {\n    (0, _jquery[\"default\"])(\".nav-tabs a:first\").tab(\"show\");\n    history.replaceState(\"\", window.document.title, window.location.pathname);\n  });\n  (0, _jquery[\"default\"])(\".challenge-solves\").click(function (_event) {\n    getSolves((0, _jquery[\"default\"])(\"#challenge-id\").val());\n  });\n  (0, _jquery[\"default\"])(\"#challenge-window\").on(\"hide.bs.modal\", function (_event) {\n    (0, _jquery[\"default\"])(\"#challenge-input\").removeClass(\"wrong\");\n    (0, _jquery[\"default\"])(\"#challenge-input\").removeClass(\"correct\");\n    (0, _jquery[\"default\"])(\"#incorrect-key\").slideUp();\n    (0, _jquery[\"default\"])(\"#correct-key\").slideUp();\n    (0, _jquery[\"default\"])(\"#already-solved\").slideUp();\n    (0, _jquery[\"default\"])(\"#too-fast\").slideUp();\n  });\n});\nsetInterval(update, 300000); // Update every 5 minutes.\n\nvar displayRessource = function displayRessource(data) {\n  (0, _ezq.ezAlert)({\n    title: \"Ressource\",\n    body: data.html,\n    button: \"Got it!\"\n  });\n};\n\nvar loadRessource = function loadRessource(id) {\n  _CTFd[\"default\"].api.get_ressource({\n    ressourceId: id\n  }).then(function (response) {\n    if (response.data.content) {\n      displayRessource(response.data);\n    }\n  });\n};\n\n//# sourceURL=webpack:///./CTFd/themes/core/assets/js/pages/challenges.js?");

/***/ })

/******/ });