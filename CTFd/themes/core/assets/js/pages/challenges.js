import "./main";
import "bootstrap/js/dist/tab";
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
let tag_list = [];

const $challenges_board = $("#challenges-board");
const $spinner_content = $challenges_board.children().detach();;

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
      .each(function(_idx) {
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
    
    // We clear the challenge list to force a reload and get the unlocked chals
    challenges = [];
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
  challenges.map(challenge => {
    if (challenge.solved_by_me) {
      const btn = $(`button[value="${challenge.id}"]`);
      btn.addClass("solved-challenge");
      btn.prepend("<i class='fas fa-check corner-button-check'></i>");
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
  update();
});

function createChalWrapper(chalinfo, catid) {
  const chalid = catid + '_' + chalinfo.name.replace(/ /g, "-").hashCode();
  const chalwrap = $("<div id='{0}' class='col-md-3 d-inline-block'></div>".format(chalid));
  let chalbutton;

  if (solves.indexOf(chalinfo.id) === -1) {
    chalbutton = $(
        "<button class='btn btn-dark challenge-button w-100 text-truncate pt-3 pb-3 mb-2' value='{0}'></button>".format(
            chalinfo.id
        )
    );
  } else {
    chalbutton = $(
        "<button class='btn btn-dark challenge-button solved-challenge w-100 text-truncate pt-3 pb-3 mb-2' value='{0}'><i class='fas fa-check corner-button-check'></i></button>".format(
            chalinfo.id
        )
    );
  }

  const chalheader = $("<p>{0}</p>".format(chalinfo.name));

  chalbutton.append(chalheader);
  chalwrap.append(chalbutton);

  $("#" + catid + "-row")
    .find(".category-challenges > .challenges-row")
    .append(chalwrap);
}

function loadChals() {
  return CTFd.api.get_challenge_list().then(function(response) {
    const categories = [];
    const challenges_filter = $("#challenges_filter option:selected").val();
    challenges = response.data;
    $challenges_board.empty();

    switch (challenges_filter) {
      case "author": {
        for (let i = challenges.length - 1; i >= 0; i--) {
          if ($.inArray(challenges[i].author_name, categories) === -1) {
            const category = challenges[i].author_name;
            categories.push(category);

            const categoryid = category.replace(/ /g, "-").hashCode();
            const categoryrow = $(
                "" +
                '<div id="{0}-row" class="pt-5">'.format(categoryid) +
                '<div class="category-header col-md-12 mb-3">' +
                "</div>" +
                '<div class="category-challenges col-md-12">' +
                '<div class="challenges-row col-md-12"></div>' +
                "</div>" +
                "</div>"
            );
            categoryrow
                .find(".category-header")
                .append($("<h3>" + category + "</h3>"));
            $challenges_board.append(categoryrow);
          }
        }

        for (let i = 0; i <= challenges.length - 1; i++) {
          const chalinfo = challenges[i];
          const catid = challenges[i].author_name.replace(/ /g, "-").hashCode();
          createChalWrapper(chalinfo, catid);
        }
        break;
      }
      case "solved": {
        categories.push("Unsolved", "Solved");

        for (const category of categories) {
          const categoryid = category.replace(/ /g, "-").hashCode();
          const categoryrow = $(
              "" +
              '<div id="{0}-row" class="pt-5">'.format(categoryid) +
              '<div class="category-header col-md-12 mb-3">' +
              "</div>" +
              '<div class="category-challenges col-md-12">' +
              '<div class="challenges-row col-md-12"></div>' +
              "</div>" +
              "</div>"
          );
          categoryrow
              .find(".category-header")
              .append($("<h3>" + category + "</h3>"));
          $challenges_board.append(categoryrow);
        }

        for (let i = 0; i <= challenges.length - 1; i++) {
          const chalinfo = challenges[i];
          const catid = challenges[i].solved_by_me
              ? "Solved".replace(/ /g, "-").hashCode()
              : "Unsolved".replace(/ /g, "-").hashCode();
          createChalWrapper(chalinfo, catid);
        }
        break;
      }
      case "name": {
        const categoryid = "names".replace(/ /g, "-").hashCode();
        const categoryrow = $(
            "" +
            '<div id="{0}-row" class="pt-5">'.format(categoryid) +
            '<div class="category-header col-md-12 mb-3">' +
            "</div>" +
            '<div class="category-challenges col-md-12">' +
            '<div class="challenges-row col-md-12"></div>' +
            "</div>" +
            "</div>"
        );
        $challenges_board.append(categoryrow);

        challenges.sort((a, b) => a.name.localeCompare(b.name));
        for (let i = 0; i <= challenges.length - 1; i++) {
          const chalinfo = challenges[i];
          createChalWrapper(chalinfo, categoryid);
        }
        break;
      }
      case "tag":
      default: {
        return CTFd.api.get_tag_list().then(function (response) {
          tag_list = response.data;
          tag_list.sort((a, b) => b.value.localeCompare(a.value));

          for (let i = tag_list.length - 1; i >= 0; i--) {
            if ($.inArray(tag_list[i].value, categories) === -1) {
              const category = tag_list[i].value;
              categories.push(category);

              const categoryid = category.replace(/ /g, "-").hashCode();
              const categoryrow = $(
                  "" +
                  '<div id="{0}-row" class="pt-5">'.format(categoryid) +
                  '<div class="category-header col-md-12 mb-3">' +
                  "</div>" +
                  '<div class="category-challenges col-md-12">' +
                  '<div class="challenges-row col-md-12"></div>' +
                  "</div>" +
                  "</div>"
              );
              categoryrow
                  .find(".category-header")
                  .append($("<h3>" + category + "</h3>"));
              $challenges_board.append(categoryrow);
            }
          }

          for (let i = 0; i <= challenges.length - 1; i++) {
            for (let j = 0; j <= challenges[i].tags.length - 1; j++) {
              const chalinfo = challenges[i];
              const catid = challenges[i].tags[j].value.replace(/ /g, "-").hashCode();
              createChalWrapper(chalinfo, catid);
            }
          }

          $(".challenge-button").click(function (_event) {
            loadChal(this.value);
          });
        });
      }
    }
    $(".challenge-button").click(function(_event) {
      loadChal(this.value);
    });
  });
}

function update() {
  $challenges_board.empty();
  $challenges_board.append($spinner_content);
  return loadChals().then(markSolves);
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
