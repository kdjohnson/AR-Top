<template>
  <div class="hero is-fullheight">
    <div class="hero-body">
      <div class="container">
        <div class="columns is-vcentered">
          <div class="column is-4 is-offset-4">

            <!-- Error message, only show this when there is an error -->
            <article class="message is-danger" v-show="error">
              <div class="message-header">
                <p>Error</p>
                <button v-on:click="closeError" class="delete" aria-label="delete"></button>
              </div>
              <div class="message-body">
                {{ error }}
              </div>
            </article>

            <div class="box">
              <h1 class="title is-4">Sign In</h1>

              <form @submit.prevent="validateBeforeSubmit">
                <!-- Email field -->
                <div class="field">
                  <label class="label">Email</label>
                  <div class="control">
                    <input
                      name="email"
                      v-model="email"
                      v-validate="emailValidator"
                      class="input"
                      type="text"
                      placeholder="Enter your email"
                      :class="{'is-danger': errors.has('email')}">
                  </div>
                  <span v-show="errors.has('email')" class="help is-danger">{{ errors.first('email') }}</span>
                </div>

                <!-- Password field -->
                <div class="field">
                  <label class="label">Password</label>
                  <div class="control">
                    <input
                      name="password"
                      v-on:keyup.enter="signin"
                      v-model="password"
                      v-validate="passwordValidator"
                      class="input"
                      type="password"
                      placeholder="Enter your password"
                      :class="{'is-danger': errors.has('password')}">
                  </div>
                  <span v-show="errors.has('password')" class="help is-danger">{{ errors.first('password') }}</span>
                </div>

                <hr>

                <!-- Buttons -->
                <div class="field">
                  <div class="control">
                    <button
                      v-on:click="signin"
                      class="button is-link"
                      type="submit"
                      :disabled="errors.any()"
                      :class="{'is-loading': loading}">
                      Sign In
                    </button>
                  </div>
                </div>
              </form>
            </div>
            <p>Need an account? <router-link to="register">Register</router-link></p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import router from './../../router/index.js'
import { mapActions } from 'vuex'
var qs = require('qs')

// Validator used for the email field
const EMAIL_VALIDATOR = {
  required: true,
  email: true,
  max: 255
}

// Validator used for the password field
const PASSWORD_VALIDATOR = {
  required: true,
  min: 8,
  max: 255
}

export default {
  name: 'Authentication',
  data: function () {
    return {
      email: '',
      password: '',
      error: '',
      loading: false,
      emailValidator: EMAIL_VALIDATOR,
      passwordValidator: PASSWORD_VALIDATOR
    }
  },
  methods: {
    ...mapActions([
      'updateUser'
    ]),
    signin: async function () {
      try {
        // Check for input validation errors before we try to authenticate
        if (this.errors.any()) {
          return
        }

        // Attempt to register the user
        this.loading = true
        let response = await axios.post('http://localhost:5000/api/auth',
          qs.stringify({
            'email': this.email,
            'password': this.password
          }))

        // Update the local user
        this.updateUser(response.data)

        // Navigate to home route
        router.push('/')
      } catch (err) {
        this.error = err.response.data.error
      }

      this.loading = false
    },

    closeError: function () {
      this.error = null
    },

    validateBeforeSubmit: function () {
      this.$validator.validateAll()
    }
  }
}
</script>

<style lang="scss" scoped>
</style>
