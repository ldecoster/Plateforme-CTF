<template>
  <div>
    <div>
      <ResourceCreationForm
        ref="ResourceCreationForm"
        :challenge_id="challenge_id"
        @refreshResources="refreshResources"
      />
    </div>

    <div>
      <ResourceEditForm
        ref="ResourceEditForm"
        :resource_id="editing_resource_id"
        @refreshResources="refreshResources"
      />
    </div>

    <table class="table table-striped">
      <thead>
        <tr>
          <td class="text-center"><b>ID</b></td>
          <td class="text-center"><b>Resource</b></td>
          <td class="text-center"><b>Settings</b></td>
        </tr>
      </thead>
      <tbody>
        <tr v-for="resource in resources" :key="resource.id">
          <td class="text-center">{{ resource.type }}</td>
          <td class="text-break">
            <pre>{{ resource.content }}</pre>
          </td>
          <td class="text-center">
            <i
              role="button"
              class="btn-fa fas fa-edit"
              @click="editResource(resource.id)"
            ></i>
            <i
              role="button"
              class="btn-fa fas fa-times"
              @click="deleteResource(resource.id)"
            ></i>
          </td>
        </tr>
      </tbody>
    </table>
    <div class="col-md-12">
      <button class="btn btn-success float-right" @click="addResource">
        Create Resource
      </button>
    </div>
  </div>
</template>

<script>
import { ezQuery } from "core/ezq";
import CTFd from "core/CTFd";
import ResourceCreationForm from "./ResourceCreationForm.vue";
import ResourceEditForm from "./ResourceEditForm.vue";
export default {
  components: {
    ResourceCreationForm,
    ResourceEditForm
  },
  props: {
    challenge_id: Number
  },
  data: function() {
    return {
      resources: [],
      editing_resource_id: null
    };
  },
  methods: {
    loadResources: function() {
      CTFd.fetch(`/api/v1/challenges/${this.$props.challenge_id}/resources`, {
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
            this.resources = response.data;
          }
        });
    },
    addResource: function() {
      let modal = this.$refs.ResourceCreationForm.$el;
      $(modal).modal();
    },
    editResource: function(resourceId) {
      this.editing_resource_id = resourceId;
      let modal = this.$refs.ResourceEditForm.$el;
      $(modal).modal();
    },
    refreshResources: function(caller) {
      this.loadResources();
      let modal;
      switch (caller) {
        case "ResourceCreationForm":
          modal = this.$refs.ResourceCreationForm.$el;
          $(modal).modal("hide");
          break;
        case "ResourceEditForm":
          modal = this.$refs.ResourceEditForm.$el;
          $(modal).modal("hide");
          break;
        default:
          break;
      }
    },
    deleteResource: function(resourceId) {
      ezQuery({
        title: "Delete Resource",
        body: "Are you sure you want to delete this resource?",
        success: () => {
          CTFd.fetch(`/api/v1/resources/${resourceId}`, {
            method: "DELETE"
          })
            .then(response => {
              return response.json();
            })
            .then(data => {
              if (data.success) {
                this.loadResources();
              }
            });
        }
      });
    }
  },
  created() {
    this.loadResources();
  }
};
</script>

<style scoped></style>