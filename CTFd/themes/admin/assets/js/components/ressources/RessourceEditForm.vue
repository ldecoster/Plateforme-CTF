<template>
  <div class="modal fade" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header text-center">
          <div class="container">
            <div class="row">
              <div class="col-md-12">
                <h3>Ressource</h3>
              </div>
            </div>
          </div>
          <button
            type="button"
            class="close"
            data-dismiss="modal"
            aria-label="Close"
          >
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        <form method="POST" @submit.prevent="updateRessource">
          <div class="modal-body">
            <div class="container">
              <div class="row">
                <div class="col-md-12">
                  <div class="form-group">
                    <label class="text-muted">
                      Ressource<br />
                      <small>Markdown &amp; HTML are supported</small>
                    </label>
                    <!-- Explicitly don't put the markdown class on this because we will add it later -->
                    <textarea
                      type="text"
                      class="form-control"
                      name="content"
                      rows="7"
                      :value="this.content"
                      ref="content"
                    ></textarea>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <div class="container">
              <div class="row">
                <div class="col-md-12">
                  <button class="btn btn-success float-right">Submit</button>
                </div>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import CTFd from "core/CTFd";
import { bindMarkdownEditor } from "../../styles";
export default {
  name: "RessourceEditForm",
  props: {
    ressource_id: Number
  },
  data: function() {
    return {
      content: null
    };
  },
  watch: {
    ressource_id: {
      immediate: true,
      handler(val, oldVal) {
        if (val !== null) {
          this.loadRessource();
        }
      }
    }
  },
  methods: {
    loadRessource: function() {
      CTFd.fetch(`/api/v1/ressources/${this.$props.ressource_id}?preview=true`, {
        method: "GET",
        credentials: "same-origin",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json"
        }
      })
        .then(response => {
          return response.json();
        })
        .then(response => {
          if (response.success) {
            let ressource = response.data;
            this.cost = ressource.cost;
            this.content = ressource.content;
            // Wait for Vue to update the DOM
            this.$nextTick(() => {
              // Wait a little longer because we need the modal to appear.
              // Kinda nasty but not really avoidable without polling the DOM via CodeMirror
              setTimeout(() => {
                let editor = this.$refs.content;
                bindMarkdownEditor(editor);
                editor.mde.codemirror.getDoc().setValue(editor.value);
                editor.mde.codemirror.refresh();
              }, 100);
            });
          }
        });
    },
    getContent: function() {
      return this.$refs.content.value;
    },
    updateRessource: function() {
      let params = {
        challenge_id: this.$props.challenge_id,
        content: this.getContent()
      };
      CTFd.fetch(`/api/v1/ressources/${this.$props.ressource_id}`, {
        method: "PATCH",
        credentials: "same-origin",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json"
        },
        body: JSON.stringify(params)
      })
        .then(response => {
          return response.json();
        })
        .then(response => {
          if (response.success) {
            this.$emit("refreshRessources", this.$options.name);
          }
        });
    }
  },
  mounted() {
    if (this.ressource_id) {
      this.loadRessource();
    }
  },
  created() {
    if (this.ressource_id) {
      this.loadRessource();
    }
  }
};
</script>

<style scoped></style>