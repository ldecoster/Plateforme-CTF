import $ from "jquery";
import CTFd from "core/CTFd";


export function deleteTag(_event) {
  const $elem = $(this);
  const tag_id = $elem.attr("tag-id");

  CTFd.api.delete_tag({ tagId: tag_id }).then(response => {
    if (response.success) {
      $elem.parent().remove();
    }
  });
}

export function setTagList(event) {

  CTFd.api.get_tag_list().then(response => {

    const tagsList = response.data;
    const $elem = $(this);
    const searchtag = $elem.val();

    //get match to the current input
    let matches = tagsList.filter(tag =>{
      const regex = new RegExp(`^${searchtag}`,'gi');
      return tag.value.match(regex);
    });
    /*if(searchtag.length === 0){
      matches = [];
      $(".list-group").html('');
    }*/

    outputHtml(matches);

    if (event.keyCode != 13) {
      return;
    }
    
    const params = {
      value: searchtag,
      challenge: window.CHALLENGE_ID
    };  
    addTag(params);  
  });
}
function addTag(params){

  CTFd.api.post_tag_list({}, params).then(response => {
    if (response.success) {
      const tpl =
        "<span class='badge badge-primary mx-1 challenge-tag'>" +
        "<span>{0}</span>" +
        "<a class='btn-fa delete-tag' tag-id='{1}'>&times;</a></span>";
      const tag = $(tpl.format(response.data.value, response.data.id));
      $("#challenge-tags").append(tag);
      // TODO: tag deletion not working on freshly created tags
      tag.click(deleteTag);
    }
  });

  $elem.val("");
}
export function addClickedTag(_event){
  $elem = $(this);
    const params = {
      id:$elem.attr("tag_id"),
      value:$elem.text(),
      challenge:window.CHALLENGE_ID
    }
  addTag(params);
}

//show result in HTML format
const outputHtml = matches =>{
  console.log(matches);
  if (matches.length > 0){
    const html = matches
    .map(
      match =>`
      <a class="list-group-item list-group-item-action list-group-item-dark" tag_id="${match.id}">${match.value}</a>
    `
    ).join('');
    $(".list-group").html(html);
  }
}