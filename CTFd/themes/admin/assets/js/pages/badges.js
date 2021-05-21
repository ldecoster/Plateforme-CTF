import "./main";
import $ from "jquery";
import { ezAlert } from "core/ezq";
import CTFd from "core/CTFd";

function deleteSelectedBadges(_event) {
  console.log("in delete badge");
  let badgeIDs = $("input[data-badge-id]:checked").map(function () {
    console.log($(this).data("badge-id"));
    return $(this).data("badge-id");
  });
  let target = badgeIDs.length === 1 ? "badge" : "badges";
  // target = "challenges"
  console.log(target);
  const reqs = [];
      for (let i=0;i<badgeIDs.length;i++) {
        console.log("bad id is"  + badgeIDs.get(i));
        reqs.push(
          CTFd.fetch(`/api/v1/badges/${badgeIDs.get(i)}`, {
            method: "DELETE"
          })
        );
      }
      Promise.all(reqs).then(_responses => {
        window.location.reload();
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

$("#edit-new-badge").on('click', function (event) {
  $("#badge-create-options").modal();
});

$("#badge-create-button").click(addBadge);

$(() => {
  $("#badges-delete-button").click(deleteSelectedBadges);
});
