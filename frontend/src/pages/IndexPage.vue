<template>
  <div class="background">
    <div class="upload-content">
      <div class="row">
        <div class="col-6" align="end">
          <q-avatar v-if="selectedPhotoURL==''" size="80px" font-size="80px" color="red" text-color="white" icon="image" class="image-icon" />
          <q-img
            v-if="selectedPhotoURL"
            :src="selectedPhotoURL"
            class="photo-preview"
          >
          </q-img>
        </div>
        <input 
          style="display: none" 
          type="file" 
          @change="onFileSelected"
          ref="photoInput">
        <q-btn
          label="Pick Photo"
          outline
          type="submit"
          class="outlined-button pick-button text-body1 text-weight-bolder"
          @keydown.enter.prevent
          @click="($refs.photoInput as any).click()"
        ></q-btn>
      </div>
      <div v-if="message" class="alert" role="alert">
        {{ message }}
      </div>
      <div class="upload-btn-position">
        <q-btn
          label="upload"
          type="submit"
          icon-right="chevron_right"
          outline
          class="outlined-button text-body1 text-weight-bolder"
          @click="savePhoto"
        ></q-btn>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import axios from 'axios';
export default defineComponent({
  name: 'IndexPage',
  components: {},
  data() {
    return {
      selectedPhoto: null as File | null,
      selectedPhotoURL: '',
      message: '',
    }
  },
  methods: {
    onFileSelected(event: Event){
      const target = event.target as HTMLInputElement;
      if(target.files != null && target.files.length >= 1) {
        this.selectedPhoto = target.files[0];
        if(this.selectedPhoto == null)
          return;
        const reader = new FileReader();
        reader.onload = (e) => {
          this.selectedPhotoURL = e.target?.result as string;
        };
        reader.readAsDataURL(this.selectedPhoto);
      }
    },
    savePhoto(){
      if(this.selectedPhoto == null) {
        this.message = 'Please choose a file first';
        return;
      }
      if(this.selectedPhoto.size > 3*1024*1024) {
        this.message = 'File too large. Max size 3 Mb';
        return;
      }
      this.uploadPhoto(this.selectedPhoto);
    },
    uploadPhoto(photo:File){
      const api = axios.create({ baseURL: 'http://localhost:8000' });
      const formData = new FormData();
      formData.append('file', photo, photo.name);
      api.post('/uploadPhoto/', formData, { headers: {
        'Content-Type': 'multipart/form-data'
      }});
    },
  },
});
</script>
<style lang="scss" scoped>
.background {
  padding: 10%;
  height: 100%;
}
.upload-content {
  align-items: center;
  justify-content: center;
  padding: 5%;
}
.image-icon{
  margin-right: 10%;
  margin-left: 10%;
}
.pick-button{
  height: 40px;
  margin-top: 15px;
  margin-bottom: 10px;
}
.alert {
  color: red;
  text-align: center;
  margin-top: 5%;
}
.upload-btn-position {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  margin-top: 5%;
}
.photo-preview {
  width: 80px;
  max-width: 100%;
  height: 80px;
  max-height: 100%;
  border-radius: 50%;
  margin-right: 10%;
  margin-left: 20%;
  border-radius: 16px;
  background: grey;
}
</style>