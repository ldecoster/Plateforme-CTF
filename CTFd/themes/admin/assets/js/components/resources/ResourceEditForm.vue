<template>
  <div class="modal fade" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header text-center">
          <div class="container">
            <div class="row">
              <div class="col-md-12">
                <h3>Resource</h3>
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
        <form method="POST" @submit.prevent="updateResource">
          <div class="modal-body">
            <div class="container">
              <div class="row">
                <div class="col-md-12">
                  <div class="form-group">
                    <label class="text-muted">
                      Resource<br />
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
  name: "ResourceEditForm",
  props: {
    resource_id: Number
  },
  data: function() {
    return {
      content: null
    };
  },
  watch: {
    resource_id: {
      immediate: true,
      handler(val, oldVal) {
        if (val !== null) {
          this.loadResource();
        }
      }
    }
  },
  methods: {
    loadResource: function() {
      CTFd.fetch(`/api/v1/resources/${this.$props.resource_id}?preview=true`, {
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
            let resource = response.data;
            this.cost = resource.cost;
            this.content = resource.content;
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
    updateResource: function() {
      let params = {
        challenge_id: this.$props.challenge_id,
        content: this.getContent()
      };
      CTFd.fetch(`/api/v1/resources/${this.$props.resource_id}`, {
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
            this.$emit("refreshResources", this.$options.name);
          }
        });
    }
  },
  mounted() {
    if (this.resource_id) {
      this.loadResource();
    }
  },
  created() {
    if (this.resource_id) {
      this.loadResource();
    }
  }
};
</script>

<style scoped></style>