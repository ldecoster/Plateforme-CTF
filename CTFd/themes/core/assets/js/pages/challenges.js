import "./main";
import "bootstrap/js/dist/tab";
import regeneratorRuntime from "regenerator-runtime";
import { ezQuery, ezAlert } from "../ezq";
import { htmlEntities } from "../utils";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import $ from "jquery";
import CTFd from "../CTFd";
import config from "../config";
import hljs from "highlight.js";

dayjs.extend(relativeTime);

CTFd._internal.challenge = {};
let challenges = [];
let solves = [];
let tagList = [];
let badgeList = {};

const loadChal = id => {
  const chal = $.grep(challenges, chal => chal.id == id)[0];

  if (chal.state === "hidden") {
    ezAlert({
      title: "Challenge Hidden!",
      body: "You haven't unlocked this challenge yet!",
      button: "Got it!"
    });
    return;
  }

  displayChal(chal);
};

const loadChalByName = name => {
  let idx = name.lastIndexOf("-");
  let pieces = [name.slice(0, idx), name.slice(idx + 1)];
  let id = pieces[1];

  const chal = $.grep(challenges, chal => chal.id == id)[0];
  displayChal(chal);
};

const displayChal = chal => {
  return Promise.all([
    CTFd.api.get_challenge({ challengeId: chal.id }),
    $.getScript(config.urlRoot + chal.script),
    $.get(config.urlRoot + chal.template)
  ]).then(responses => {
    const challenge = CTFd._internal.challenge;

    $("#challenge-window").empty();

    // Inject challenge data into the plugin
    challenge.data = responses[0].data;

    // Call preRender function in plugin
    challenge.preRender();

    // Build HTML from the Jinja response in API
    $("#challenge-window").append(responses[0].data.view);

    $("#challenge-window #challenge-input").addClass("form-control");
    $("#challenge-window #challenge-submit").addClass(
      "btn btn-md btn-outline-secondary float-right"
    );

    let modal = $("#challenge-window").find(".modal-dialog");
    if (
      window.init.theme_settings &&
      window.init.theme_settings.challenge_window_size
    ) {
      switch (window.init.theme_settings.challenge_window_size) {
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

    $(".challenge-solves").click(function (_event) {
      getSolves($("#challenge-id").val());
    });
    $(".nav-tabs a").click(function (event) {
      event.preventDefault();
      $(this).tab("show");
    });

    // Handle modal toggling
    $("#challenge-window").on("hide.bs.modal", function (_event) {
      $("#challenge-input").removeClass("wrong");
      $("#challenge-input").removeClass("correct");
      $("#incorrect-key").slideUp();
      $("#correct-key").slideUp();
      $("#already-solved").slideUp();
      $("#too-fast").slideUp();
    });

    $(".load-hint").on("click", function (_event) {
      loadHint($(this).data("hint-id"));
    });

    $("#challenge-submit").click(function (event) {
      event.preventDefault();
      $("#challenge-submit").addClass("disabled-button");
      $("#challenge-submit").prop("disabled", true);
      CTFd._internal.challenge
        .submit()
        .then(renderSubmissionResponse)
        .then(loadChals)
        .then(markSolves);
    });

    $("#challenge-input").keyup(event => {
      if (event.keyCode == 13) {
        $("#challenge-submit").click();
      }
    });

    challenge.postRender();

    $("#challenge-window")
      .find("pre code")
      .each(function (_idx) {
        hljs.highlightBlock(this);
      });

    window.location.replace(
      window.location.href.split("#")[0] + `#${chal.name}-${chal.id}`
    );
    $("#challenge-window").modal();
  });
};

function renderSubmissionResponse(response) {
  const result = response.data;

  const result_message = $("#result-message");
  const result_notification = $("#result-notification");
  const answer_input = $("#challenge-input");
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
    // Challenge Solved
    result_notification.addClass(
      "alert alert-success alert-dismissable text-center"
    );
    result_notification.slideDown();

    if (
      $(".challenge-solves")
        .text()
        .trim()
    ) {
      // Only try to increment solves if the text isn't hidden
      $(".challenge-solves").text(
        parseInt(
          $(".challenge-solves")
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
    // Challenge already solved
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
    $("#challenge-submit").removeClass("disabled-button");
    $("#challenge-submit").prop("disabled", false);
  }, 3000);
}

function markSolves() {
  return CTFd.api.get_user_solves({ userId: "me" }).then(function (response) {
    const solves = response.data;
    for (let i = solves.length - 1; i >= 0; i--) {
      const btn = $('button[value="' + solves[i].challenge_id + '"]');
      btn.addClass("solved-challenge");
      btn.prepend("<i class='fas fa-check corner-button-check'></i>");
    }
  });
}

function loadUserSolves() {
  if (CTFd.user.id == 0) {
    return Promise.resolve();
  }

  return CTFd.api.get_user_solves({ userId: "me" }).then(function (response) {
    solves = response.data;

    for (let i = solves.length - 1; i >= 0; i--) {
      const chal_id = solves[i].challenge_id;
      solves.push(chal_id);
    }
  });
}

function getSolves(id) {
  return CTFd.api.get_challenge_solves({ challengeId: id }).then(response => {
    const data = response.data;
    $(".challenge-solves").text(parseInt(data.length) + " Solves");
    const box = $("#challenge-solves-names");
    box.empty();
    for (let i = 0; i < data.length; i++) {
      const id = data[i].account_id;
      const name = data[i].name;
      const date = dayjs(data[i].date).fromNow();
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

// todo ISEN : fix async issue with dependencies
async function loadChals() {
  //Add loading spinner while fetching API
  $("#challenges-board").empty();
  $("#challenges-board").append(
    $(
      "" +
      '<div class="min-vh-50 d-flex align-items-center">' +
      '<div class="text-center w-100">' +
      '<i class="fas fa-circle-notch fa-spin fa-3x fa-fw spinner"></i>' +
      '</div>' +
      '</div>'
    ));
  if (challenges.length === 0) {
    challenges = (await CTFd.api.get_challenge_list()).data;
  }
  if (tagList.length === 0) {
    tagList = (await CTFd.api.get_tag_list()).data;
  }
  if (badgeList.length === 0) {
    console.log("get badge list");
    let response = (await CTFd.api.get_badge_list()).data;
    response.forEach(badge => {
      badgeList[badge.tag_id] = badge.name;
    });
    console.log(badgeList);
  }

  loadUserSolves().then(async function () {
    const challengesBoard = $("<div></div>");
    let orderValue = $("#challenges_filter option:selected").val();

    //Set up default tag/challenge values.
    if (orderValue === undefined) {
      orderValue = "tag";
    }

    //Display tag/challenge sorted by values
    else if (orderValue === "tag") {
      tagList.sort((a, b) => a.value.localeCompare(b.value))
      tagList.reverse();
      for (let i = tagList.length - 1; i >= 0; i--) {
        let isExoSolved = true;
        const ID = tagList[i].value.replace(/ /g, "-").hashCode();
        const tagrow = $(
          "" +
          '<div id="{0}-row" class="pt-5">'.format(ID) +
          '<div class="title-row">' +
          '<div class="tag-header col-md-12 mb-3">' +
          "</div>" +
          '<div class="exercise-badge col-md-12 my-1">' +
          '</div>' +
          '</div>' +
          '<div class="tag-challenge col-md-12">' +
          '<div class="challenges-row col-md-12"></div>' +
          "</div>" +
          "</div>"
        );
        tagrow
          .find(".tag-header")
          .append($("<h3>" + tagList[i].value + "</h3>"));
        challengesBoard.append(tagrow);

        //This part add the badge next to its associated tag
        //,if this one is an exercise. It also
        //check if the exercise is solved or not.
        if (tagList[i].exercise) {
          let chalsIds = tagList[i].challenges;
          for (let k = 0; k < chalsIds.length; k++) {
            if (solves.indexOf(chalsIds[k]) < 0 ) {
              isExoSolved = false;
              break;
            }
          }
          const badge = $(
            '<span class="badge {0} mx-1 challenge-tag">'.format(isExoSolved  ? 'badge-success' : 'badge-warning') +
            '<span>{0}</span>'.format(isExoSolved ? 'Solved exercise' : 'Unsolved Exercise') +
            '</span>'
          );
          if (chalsIds.length > 0) {
            tagrow
              .find(".exercise-badge")
              .append(badge);
          }
        }
      }
      for (let i = 0; i < challenges.length; i++) {
        for (let j = 0; j < challenges[i].tags.length; j++) {
          const chalinfo = challenges[i];
          const chalid = chalinfo.name.replace(/ /g, "-").hashCode();
          const tagID = challenges[i].tags[j].value.replace(/ /g, "-").hashCode();
          const chalwrap = $(
            "<div id='{0}' class='col-md-3 d-inline-block'></div>".format(chalid)
          );
          let chalbutton;

          if (solves.indexOf(chalinfo.id) === -1) {
            chalbutton = $(
              "<button class='btn btn-dark challenge-button w-100 text-truncate pt-3 pb-3 mb-2' value='{0}'></button>".format(
                chalinfo.id
              )
            );
          } else {
            isExoSolved = false;
            chalbutton = $(
              "<button class='btn btn-dark challenge-button solved-challenge w-100 text-truncate pt-3 pb-3 mb-2' value='{0}'><i class='fas fa-check corner-button-check'></i></button>".format(
                chalinfo.id
              )
            );
          }

          const chalheader = $("<p>{0}</p>".format(chalinfo.name));
          for (let j = 0; j < chalinfo.tags.length; j++) {
            const tag = "tag-" + chalinfo.tags[j].value.replace(/ /g, "-");
            chalwrap.addClass(tag);
          }

          chalbutton.append(chalheader);
          chalwrap.append(chalbutton);

          challengesBoard
            .find("#" + tagID + "-row > .tag-challenge > .challenges-row")
            .append(chalwrap);
        }
      }
    }

    //Display challenges sorted by name
    else if (orderValue === "name") {
      challenges.sort((a, b) => a.name.localeCompare(b.name))
      challenges.reverse();
      for (let i = challenges.length - 1; i >= 0; i--) {
        const chalinfo = challenges[i];

        if (solves.indexOf(chalinfo.id) === -1) {
          const chalrow = $(
            "" +
            '<button class="btn btn-dark challenge-button w-100 text-truncate col-md-3" style="margin-right:1rem; margin-top:2rem" value="{0}"></button>'.format(
              chalinfo.id
            )
            + "</div>"
          );

          chalrow.append($("<h3>" + challenges[i].name + "</h3>"));
          challengesBoard.append(chalrow);
        }
        else if (solves.indexOf(chalinfo.id) !== -1) {
          const chalrow = $(
            "" +
            '<button class="btn btn-dark challenge-button w-100 solved-challenge text-truncate col-md-3" style="margin-right:1rem; margin-top:2rem" value="{0}"></button>'.format(
              chalinfo.id
            )
          );

          chalrow.append($("<h3>" + challenges[i].name + "</h3>"));
          challengesBoard.append(chalrow);
        }
      }
    }

    //Display challenges sorted by solved or not
    else if (orderValue === "solved") {
      challenges.sort((a, b) => a.name.localeCompare(b.name))
      challenges.reverse();
      const chalrow = $(
        "" +
        '<div class="solved-header col-md-12 mb-3">' +
        "<h3> Solved </h3>" +
        '<div class="challenges-row col-md-12"></div>' +
        "</div>" +
        '<div class="unsolved-header col-md-12 mb-3">' +
        "<h3> Unsolved </h3>" +
        '<div class="challenges-row col-md-12"></div>' +
        "</div>"
      );
      challengesBoard.append(chalrow);
      for (let i = challenges.length - 1; i >= 0; i--) {
        const chalinfo = challenges[i];
        const chalid = chalinfo.name.replace(/ /g, "-").hashCode();
        let classValue;
        const chalwrap = $(
          "<div id='{0}' class='col-md-3 d-inline-block'></div>".format(chalid)
        );
        let chalbutton;

        if (solves.indexOf(chalinfo.id) === -1) {
          chalbutton = $(
            "<button class='btn btn-dark challenge-button w-100 text-truncate pt-3 pb-3 mb-2' value='{0}'></button>".format(
              chalinfo.id
            )
          );
          classValue = ".unsolved-header";

        } else {
          chalbutton = $(
            "<button class='btn btn-dark challenge-button solved-challenge w-100 text-truncate pt-3 pb-3 mb-2' value='{0}'><i class='fas fa-check corner-button-check'></i></button>".format(
              chalinfo.id
            )
          );
          classValue = ".solved-header";
        }
        const chalheader = $("<p>{0}</p>".format(chalinfo.name));
        chalbutton.append(chalheader);
        chalwrap.append(chalbutton);
        challengesBoard
          .find(classValue + " > .challenges-row")
          .append(chalwrap);
      }
    }

    //Display challenges sorted by author
    else if (orderValue === "author") {
      const authorList = [];
      for (let i = 0; i < challenges.length; i++) {
        const chalwrap = $(
          "<div id='{0}' class='col-md-3 d-inline-block'></div>".format(challenges[i].id)
        );
        if (authorList.indexOf(challenges[i].authorId) === -1) {
          authorList.push(challenges[i].authorId);
          let user = (await CTFd.api.get_user_public({ userId: challenges[i].authorId })).data;
          const chalrow = $(
            "" +
            '<div id="{0}-row" class="pt-5">'.format(challenges[i].authorId) +
            '<div class="author-header col-md-12 mb-3">' +
            "</div>" +
            '<div class="author-challenge col-md-12">' +
            '<div class="challenges-row col-md-12"></div>' +
            "</div>" +
            "</div>"
          );
          chalrow
            .find(".author-header")
            .append($("<h3>" + user.name + "</h3>"));
          challengesBoard.append(chalrow);
        }
        let chalbutton;
        if (solves.indexOf(challenges[i].id) === -1) {
          chalbutton = $(
            "<button class='btn btn-dark challenge-button w-100 text-truncate pt-3 pb-3 mb-2' value='{0}'></button>".format(
              challenges[i].id
            )
          );
        } else {
          chalbutton = $(
            "<button class='btn btn-dark challenge-button solved-challenge w-100 text-truncate pt-3 pb-3 mb-2' value='{0}'><i class='fas fa-check corner-button-check'></i></button>".format(
              challenges[i].id
            )
          );
        }
        const chalheader = $("<p>{0}</p>".format(challenges[i].name));
        chalbutton.append(chalheader);
        chalwrap.append(chalbutton);
        challengesBoard
          .find("#" + challenges[i].authorId + "-row > .author-challenge > .challenges-row")
          .append(chalwrap);
      }
    }
    $("#challenges-board").empty();
    $("#challenges-board").append(challengesBoard);
    $(".challenge-button").click(function (_event) {
      loadChal(this.value);
      getSolves(this.value);
    });
  });

}

function update() {
  return loadUserSolves() // Load the user's solved challenge ids
    .then(loadChals) //  Load the full list of challenges
    .then(markSolves);
}

$(() => {
  update().then(() => {
    if (window.location.hash.length > 0) {
      loadChalByName(decodeURIComponent(window.location.hash.substring(1)));
    }
  });

  $("#challenge-input").keyup(function (event) {
    if (event.keyCode == 13) {
      $("#challenge-submit").click();
    }
  });

  $(".nav-tabs a").click(function (event) {
    event.preventDefault();
    $(this).tab("show");
  });

  $("#challenge-window").on("hidden.bs.modal", function (_event) {
    $(".nav-tabs a:first").tab("show");
    history.replaceState("", window.document.title, window.location.pathname);
  });

  $(".challenge-solves").click(function (_event) {
    getSolves($("#challenge-id").val());
  });

  $("#challenge-window").on("hide.bs.modal", function (_event) {
    $("#challenge-input").removeClass("wrong");
    $("#challenge-input").removeClass("correct");
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
          body: "",
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
