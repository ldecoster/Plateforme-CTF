import "./main";
import regeneratorRuntime from "regenerator-runtime";
import $ from "jquery";
import { ezAlert, ezQuery } from "core/ezq";
import CTFd from "core/CTFd";

let solves = [];

function deleteSelectedBadges(_event) {
  let badgeIDs = $("input[data-badge-id]:checked").map(function () {
    return $(this).data("badge-id");
  });
  let target = badgeIDs.length === 1 ? "badge" : "badges";

  ezQuery({
    title: "Delete Badges",
    body: `Are you sure you want to delete ${badgeIDs.length} ${target}?`,
    success: function () {
      const reqs = [];
      for (var badID of badgeIDs) {
        reqs.push(
          CTFd.fetch(`/api/v1/badges/${badID}`, {
            method: "DELETE"
          })
        );
      }
      Promise.all(reqs).then(_responses => {
        window.location.reload();
      });
    }
  });
}


function addBadge(_event) {

  let badge_name = document.getElementsByName("badge_name")[0].value;
  let badge_desc = document.getElementsByName("badge_desc")[0].value;
  let badge_tag = document.getElementsByName("badge_tag")[0].value;

  CTFd.api.get_tag_list().then(response => {
    let tagList = response.data;
    let matches = tagList.filter(tag => {
      return tag.value.match(badge_tag);
    });
    let tag_id = matches[0].id;

    const params = {
      name: badge_name,
      description: badge_desc,
      tag_id: tag_id,
    };

    CTFd.fetch("/api/v1/badges", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify(params)
    }).then(response => {
      if (response.status === 200) {
        $("#badge-create-options").modal('hide');
        window.location.reload();
      }
      return;
    });
  });

}

function bulkEditBadges(_event) {
  let badgeIDs = $("input[data-badge-id]:checked").map(function () {
    return $(this).data("badge-id");
  });

  ezAlert({
    title: "Edit Badges",
    body: $(`
    <form id="badges-bulk-edit">
      <div class="form-group">
        <label>State</label>
        <select name="state" data-initial="">
          <option value="">--</option>
          <option value="hidden">Hidden</option>
          <option value="visible">Visible</option>
          <option value="voting">Voting</option>
        </select>
      </div>
    </form>
    `),
    button: "Submit",
    success: function () {
      let data = $("#badges-bulk-edit").serializeJSON(true);
      const reqs = [];
      for (var badID of badgeIDs) {
        reqs.push(
          CTFd.fetch(`/api/v1/badges/${badID}`, {
            method: "PATCH",
            body: JSON.stringify(data)
          })
        );
      }
      Promise.all(reqs).then(_responses => {
        window.location.reload();
      });
    }
  });
}
function loadUserSolves() {
  return CTFd.api.get_user_solves({ userId: "me" }).then(function (response) {
    temp = response.data;
    for (let i = temp.length - 1; i >= 0; i--) {
      const chal_id = temp[i].challenge_id;
      solves.push(chal_id);
    }
  });
}

async function loadBadgeProgressBar() {
  const badges = (await CTFd.api.get_badge_list()).data;
  loadUserSolves().then(async function (){
    const users = (await CTFd.api.get_user_list()).data;
    for (let i = 0; i < badges.length; i++) {
      let solvers = 0;
      let numOfSolvedChal = 0;
      const challenges = (await CTFd.api.get_tagChallenge_byTagId({ tagId: badges[i].tag_id })).data;
      const tag = (await CTFd.api.get_tag({tagId:badges[i].tag_id})).data;
      for (let i =0; i< users.length; i++){
        const user_solves = (CTFd.api.get_user_solves({ userId: users[i].id })).data
      }
      for (let j = 0; j < challenges.length; j++) {
        if (solves.indexOf(challenges[j].challenge_id) >= 0) {
          numOfSolvedChal++;
        }
      }
      const progress = (challenges.length !== 0 ? numOfSolvedChal / challenges.length : 0) * 100;
      const progressBar = $(
        '<div class="progress-bar {0}" role="progressbar"'.format(progress === 100 ? 'bg-success' : '') +
        'aria-valuenow="{0}" aria-valuemin="0"'.format(numOfSolvedChal) +
        'aria-valuemax="{0}" style="width:{1}%">'.format(challenges.length, progress) +
        '{0}'.format(progress !== 0 ? progress + '%' : '') +
        '</div>'
      );
      const tagClass = progress===100?' badge-success':' badge-primary';
      $("#" + badges[i].id + "-progress").append(progressBar);
  
      const tagItem = $(
        '<span class="badge {0} mx-1 challenge-tag">'.format(progress !==100?"badge-primary":"badge-success")+
        '<span>{0}</span>'.format(tag.value)+
        '</span>'
      );
      $("#" + badges[i].id + "-tag").append(tagItem);
    }
  });
}

$("#edit-new-badge").on('click', function (event) {
  $("#badge-create-options").modal();
});

$("#badge-create-button").click(addBadge);

$(() => {
  loadBadgeProgressBar();
  $("#badges-delete-button").click(deleteSelectedBadges);
  $("#badges-edit-button").click(bulkEditBadges);
});
