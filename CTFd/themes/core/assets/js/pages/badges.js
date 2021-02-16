import "./main";
import "bootstrap/js/dist/tab";
import regeneratorRuntime from "regenerator-runtime";
import { ezQuery, ezAlert } from "../ezq";
import { htmlEntities } from "../utils";
import Moment from "moment";
import $ from "jquery";
import CTFd from "../CTFd";
import config from "../config";

const api_func = {
  teams: x => CTFd.api.get_team_solves({ teamId: x }),
  users: x => CTFd.api.get_user_solves({ userId: x })
};

CTFd._internal.badge = {};
let badges = [];
let solves = [];
let tagList = [];
const loadBad = id => {
  const bad = $.grep(badges, bad => bad.id == id)[0];

  if (bad.state === "hidden") {
    ezAlert({
      title: "badge Hidden!",
      body: "You haven't unlocked this badge yet!",
      button: "Got it!"
    });
    return;
  }

  displayBad(bad);
};


const displayBad = bad => {
  return Promise.all([
    CTFd.api.get_badge({ badgeId: bad.id }),
    $.getScript(config.urlRoot + bad.script),
    $.get(config.urlRoot + bad.template)
  ]).then(responses => {
    const badge = CTFd._internal.badge;

    $("#badge-window").empty();

    // Inject badge data into the plugin
    badge.data = responses[0].data;

    // Call preRender function in plugin
    badge.preRender();

    // Build HTML from the Jinja response in API
    $("#badge-window").append(responses[0].data.view);

    $("#badge-window #badge-input").addClass("form-control");
    $("#badge-window #badge-submit").addClass(
      "btn btn-md btn-outline-secondary float-right"
    );

    let modal = $("#badge-window").find(".modal-dialog");
    if (
      window.init.theme_settings &&
      window.init.theme_settings.badge_window_size
    ) {
      switch (window.init.theme_settings.badge_window_size) {
        case "sm":
          modal.addClass("modal-sm");
          break;
        case "lg":
          modal.addClass("modal-lg");
          break;
        case "xl":
          modal.addClass("modal-xl");
          break;
        default:
          break;
      }
    }

    $(".badge-solves").click(function (_event) {
      getSolves($("#badge-id").val());
    });
    $(".nav-tabs a").click(function (event) {
      event.preventDefault();
      $(this).tab("show");
    });

    // Handle modal toggling
    $("#badge-window").on("hide.bs.modal", function (_event) {
      $("#badge-input").removeClass("wrong");
      $("#badge-input").removeClass("correct");
      $("#incorrect-key").slideUp();
      $("#correct-key").slideUp();
      $("#already-solved").slideUp();
      $("#too-fast").slideUp();
    });

    $(".load-hint").on("click", function (_event) {
      loadHint($(this).data("hint-id"));
    });

    $("#badge-submit").click(function (event) {
      event.preventDefault();
      $("#badge-submit").addClass("disabled-button");
      $("#badge-submit").prop("disabled", true);
      CTFd._internal.badge
        .submit()
        .then(renderSubmissionResponse)
        .then(loadChals)
        .then(markSolves);
    });

    $("#badge-input").keyup(event => {
      if (event.keyCode == 13) {
        $("#badge-submit").click();
      }
    });

    badge.postRender();

    window.location.replace(
      window.location.href.split("#")[0] + `#${chal.name}-${chal.id}`
    );
    $("#badge-window").modal();
  });
};

function renderSubmissionResponse(response) {
  const result = response.data;

  const result_message = $("#result-message");
  const result_notification = $("#result-notification");
  const answer_input = $("#badge-input");
  result_notification.removeClass();
  result_message.text(result.message);

  if (result.status === "authentication_required") {
    window.location =
      CTFd.config.urlRoot +
      "/login?next=" +
      CTFd.config.urlRoot +
      window.location.pathname +
      window.location.hash;
    return;
  } else if (result.status === "incorrect") {
    // Incorrect key
    result_notification.addClass(
      "alert alert-danger alert-dismissable text-center"
    );
    result_notification.slideDown();

    answer_input.removeClass("correct");
    answer_input.addClass("wrong");
    setTimeout(function () {
      answer_input.removeClass("wrong");
    }, 3000);
  } else if (result.status === "correct") {
    // badge Solved
    result_notification.addClass(
      "alert alert-success alert-dismissable text-center"
    );
    result_notification.slideDown();

    if (
      $(".badge-solves")
        .text()
        .trim()
    ) {
      // Only try to increment solves if the text isn't hidden
      $(".badge-solves").text(
        parseInt(
          $(".badge-solves")
            .text()
            .split(" ")[0]
        ) +
        1 +
        " Solves"
      );
    }

    answer_input.val("");
    answer_input.removeClass("wrong");
    answer_input.addClass("correct");
  } else if (result.status === "already_solved") {
    // badge already solved
    result_notification.addClass(
      "alert alert-info alert-dismissable text-center"
    );
    result_notification.slideDown();

    answer_input.addClass("correct");
  } else if (result.status === "paused") {
    // CTF is paused
    result_notification.addClass(
      "alert alert-warning alert-dismissable text-center"
    );
    result_notification.slideDown();
  } else if (result.status === "ratelimited") {
    // Keys per minute too high
    result_notification.addClass(
      "alert alert-warning alert-dismissable text-center"
    );
    result_notification.slideDown();

    answer_input.addClass("too-fast");
    setTimeout(function () {
      answer_input.removeClass("too-fast");
    }, 3000);
  }
  setTimeout(function () {
    $(".alert").slideUp();
    $("#badge-submit").removeClass("disabled-button");
    $("#badge-submit").prop("disabled", false);
  }, 3000);
}

function markSolves() {
  return api_func[CTFd.config.userMode]("me").then(function (response) {
    const solves = response.data;
    for (let i = solves.length - 1; i >= 0; i--) {
      const btn = $('button[value="' + solves[i].badge_id + '"]');
      btn.addClass("solved-badge");
      btn.prepend("<i class='fas fa-check corner-button-check'></i>");
    }
  });
}

function loadUserSolves() {
  if (CTFd.user.id == 0) {
    return Promise.resolve();
  }

  return api_func[CTFd.config.userMode]("me").then(function (response) {
    solves = response.data;

    for (let i = solves.length - 1; i >= 0; i--) {
      const chal_id = solves[i].badge_id;
      solves.push(chal_id);
    }
  });
}

function getSolves(id) {
  return CTFd.api.get_badge_solves({ badgeId: id }).then(response => {
    const data = response.data;
    $(".badge-solves").text(parseInt(data.length) + " Solves");
    const box = $("#badge-solves-names");
    box.empty();
    for (let i = 0; i < data.length; i++) {
      const id = data[i].account_id;
      const name = data[i].name;
      const date = Moment(data[i].date)
        .local()
        .fromNow();
      const account_url = data[i].account_url;
      box.append(
        '<tr><td><a href="{0}">{2}</td><td>{3}</td></tr>'.format(
          account_url,
          id,
          htmlEntities(name),
          date
        )
      );
    }
  });
}

$('select').on('change', function () {
  loadChals();
});

async function loadChals() {
  if (badges.length === 0) {
    badges = (await CTFd.api.get_badge_list()).data;
  }
  if (tagList.length === 0) {
    tagList = (await CTFd.api.get_tag_list()).data;
  }

  loadUserSolves().then(function (solvedbadges) {

    const $badges_board = $("#badges-board");
    $badges_board.empty();
    const orderValue = $("#badges_filter option:selected").val();

    //Set up default tag/badge values.
    if (orderValue === undefined)
      orderValue = "default"

    //Display default tag/badge values.
    if (orderValue == "default") {
      for (let i = tagList.length - 1; i >= 0; i--) {
        const ID = tagList[i].value.replace(/ /g, "-").hashCode();
        const tagrow = $(
          "" +
          '<div id="{0}-row" class="pt-5">'.format(ID) +
          '<div class="tag-header col-md-12 mb-3">' +
          "</div>" +
          '<div class="tag-badge col-md-12">' +
          '<div class="badges-row col-md-12"></div>' +
          "</div>" +
          "</div>"
        );
        tagrow
          .find(".tag-header")
          .append($("<h3>" + tagList[i].value + "</h3>"));
        $badges_board.append(tagrow);
      }
    }

    //Display tag/badge sorted by values
    else if (orderValue == "tag") {
      tagList.sort((a, b) => a.value.localeCompare(b.value))
      tagList.reverse();
      for (let i = tagList.length - 1; i >= 0; i--) {
        //for (let i = 0; i <=tagList.length ; i++) {
        const ID = tagList[i].value.replace(/ /g, "-").hashCode();
        const tagrow = $(
          "" +
          '<div id="{0}-row" class="pt-5">'.format(ID) +
          '<div class="tag-header col-md-12 mb-3">' +
          "</div>" +
          '<div class="tag-badge col-md-12">' +
          '<div class="badges-row col-md-12"></div>' +
          "</div>" +
          "</div>"
        );
        tagrow
          .find(".tag-header")
          .append($("<h3>" + tagList[i].value + "</h3>"));
        $badges_board.append(tagrow);
      }
    }

    //Display badges sorted by name
    else if (orderValue == "name") {
      badges.sort((a, b) => a.name.localeCompare(b.name))
      badges.reverse();
      for (let i = badges.length - 1; i >= 0; i--) {
        const chalinfo = badges[i];

        if (solves.indexOf(chalinfo.id) == -1) {
          const chalrow = $(
            "" +
            '<button class="btn btn-dark badge-button w-100 text-truncate col-md-3" style="margin-right:1rem; margin-top:2rem" value="{0}"></button>'.format(
              chalinfo.id
            )
            + "</div>"
          );

          chalrow.append($("<h3>" + badges[i].name + "</h3>"));
          $badges_board.append(chalrow);
        }
        else if (solves.indexOf(chalinfo.id) !== -1) {
          const chalrow = $(
            "" +
            '<button class="btn btn-dark badge-button w-100 solved-badge text-truncate col-md-3" style="margin-right:1rem; margin-top:2rem" value="{0}"></button>'.format(
              chalinfo.id
            )
          );

          chalrow.append($("<h3>" + badges[i].name + "</h3>"));
          $badges_board.append(chalrow);
        }
      }
    }

    //Display badges sorted by solved or not
    else if (orderValue == "solved") {
      badges.sort((a, b) => a.name.localeCompare(b.name))
      badges.reverse();
      const chalrow = $(
        "" +
        '<div class="solved-header col-md-12 mb-3">' +
        "<h3> Solved </h3>" +
        '<div class="badges-row col-md-12"></div>' +
        "</div>" +
        '<div class="unsolved-header col-md-12 mb-3">' +
        "<h3> Unsolved </h3>" +
        '<div class="badges-row col-md-12"></div>' +
        "</div>"
      );
      $badges_board.append(chalrow);
      for (let i = badges.length - 1; i >= 0; i--) {
        const chalinfo = badges[i];
        const chalid = chalinfo.name.replace(/ /g, "-").hashCode();
        const chalwrap = $(
          "<div id='{0}' class='col-md-3 d-inline-block'></div>".format(chalid)
        );
        let chalbutton;

        if (solves.indexOf(chalinfo.id) == -1) {
          chalbutton = $(
            "<button class='btn btn-dark badge-button w-100 text-truncate pt-3 pb-3 mb-2' value='{0}'></button>".format(
              chalinfo.id
            )
          );
          const chalheader = $("<p>{0}</p>".format(chalinfo.name));
          const chalscore = $("<span>{0}</span>".format(chalinfo.value));
          chalbutton.append(chalheader);
          chalbutton.append(chalscore);
          chalwrap.append(chalbutton);
          $(".unsolved-header")
            .find(".badges-row")
            .append(chalwrap);
        } else {
          chalbutton = $(
            "<button class='btn btn-dark badge-button solved-badge w-100 text-truncate pt-3 pb-3 mb-2' value='{0}'><i class='fas fa-check corner-button-check'></i></button>".format(
              chalinfo.id
            )
          );
          const chalheader = $("<p>{0}</p>".format(chalinfo.name));
          const chalscore = $("<span>{0}</span>".format(chalinfo.value));
          chalbutton.append(chalheader);
          chalbutton.append(chalscore);
          chalwrap.append(chalbutton);
          $(".solved-header")
            .find(".badges-row")
            .append(chalwrap);
        }
      }
    }

    for (let i = 0; i < badges.length; i++) {
      for (let j = 0; j < badges[i].tags.length; j++) {
        const chalinfo = badges[i];
        const chalid = chalinfo.name.replace(/ /g, "-").hashCode();
        const tagID = badges[i].tags[j].value.replace(/ /g, "-").hashCode();
        const chalwrap = $(
          "<div id='{0}' class='col-md-3 d-inline-block'></div>".format(chalid)
        );
        let chalbutton;

        if (solves.indexOf(chalinfo.id) == -1) {
          chalbutton = $(
            "<button class='btn btn-dark badge-button w-100 text-truncate pt-3 pb-3 mb-2' value='{0}'></button>".format(
              chalinfo.id
            )
          );
        } else {
          chalbutton = $(
            "<button class='btn btn-dark badge-button solved-badge w-100 text-truncate pt-3 pb-3 mb-2' value='{0}'><i class='fas fa-check corner-button-check'></i></button>".format(
              chalinfo.id
            )
          );
        }

        const chalheader = $("<p>{0}</p>".format(chalinfo.name));
        const chalscore = $("<span>{0}</span>".format(chalinfo.value));
        for (let j = 0; j < chalinfo.tags.length; j++) {
          const tag = "tag-" + chalinfo.tags[j].value.replace(/ /g, "-");
          chalwrap.addClass(tag);
        }

        chalbutton.append(chalheader);
        chalbutton.append(chalscore);
        chalwrap.append(chalbutton);


        $("#" + tagID + "-row")
          .find(".tag-badge > .badges-row")
          .append(chalwrap);
      }
    }
    $(".badge-button").click(function (_event) {
      loadChal(this.value);
      getSolves(this.value);
    });
  });

}



function update() {
  return loadUserSolves() // Load the user's solved badge ids
    .then(loadChals) //  Load the full list of badges
    .then(markSolves);
}

$(() => {
  update().then(() => {
    if (window.location.hash.length > 0) {
      loadChalByName(decodeURIComponent(window.location.hash.substring(1)));
    }
  });

  $("#badge-input").keyup(function (event) {
    if (event.keyCode == 13) {
      $("#badge-submit").click();
    }
  });

  $(".nav-tabs a").click(function (event) {
    event.preventDefault();
    $(this).tab("show");
  });

  $("#badge-window").on("hidden.bs.modal", function (_event) {
    $(".nav-tabs a:first").tab("show");
    history.replaceState("", window.document.title, window.location.pathname);
  });

  $(".badge-solves").click(function (_event) {
    getSolves($("#badge-id").val());
  });

  $("#badge-window").on("hide.bs.modal", function (_event) {
    $("#badge-input").removeClass("wrong");
    $("#badge-input").removeClass("correct");
    $("#incorrect-key").slideUp();
    $("#correct-key").slideUp();
    $("#already-solved").slideUp();
    $("#too-fast").slideUp();
  });
});
setInterval(update, 300000); // Update every 5 minutes.

const displayHint = data => {
  ezAlert({
    title: "Hint",
    body: data.html,
    button: "Got it!"
  });
};

const displayUnlock = id => {
  ezQuery({
    title: "Unlock Hint?",
    body: "Are you sure you want to open this hint?",
    success: () => {
      const params = {
        target: id,
        type: "hints"
      };
      CTFd.api.post_unlock_list({}, params).then(response => {
        if (response.success) {
          CTFd.api.get_hint({ hintId: id }).then(response => {
            displayHint(response.data);
          });

          return;
        }

        ezAlert({
          title: "Error",
          body: response.errors.score,
          button: "Got it!"
        });
      });
    }
  });
};

const loadHint = id => {
  CTFd.api.get_hint({ hintId: id }).then(response => {
    if (response.data.content) {
      displayHint(response.data);
      return;
    }

    displayUnlock(id);
  });
};
