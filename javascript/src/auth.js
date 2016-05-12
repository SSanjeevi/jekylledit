/**
 *
 * @author petr.sloup@klokantech.com (Petr Sloup)
 *
 * Copyright 2016 Klokan Technologies Gmbh (www.klokantech.com)
 */
goog.provide('klokantech.jekylledit.Auth');

goog.require('goog.dom');
goog.require('goog.events');
goog.require('goog.events.EventType');
goog.require('goog.net.XhrIo');



/**
 * @param {Element} parentElement
 * @constructor
 */
klokantech.jekylledit.Auth = function(parentElement) {
  /**
   * @type {?string}
   * @private
   */
  this.accessToken_ = null;

  /**
   * @type {Element}
   * @private
   */
  this.parentElement_ = parentElement;

  /**
   * @type {Element}
   * @private
   */
  this.element_ = goog.dom.createDom(goog.dom.TagName.DIV, 'je-auth');
};


/**
 * @return {Element}
 */
klokantech.jekylledit.Auth.prototype.getElement = function() {
  return this.element_;
};


/**
 * @private
 */
klokantech.jekylledit.Auth.prototype.replaceWithSpinner_ = function() {
  goog.dom.removeChildren(this.element_);
  goog.dom.appendChild(this.element_,
                       goog.dom.createDom(goog.dom.TagName.DIV, 'je-spinner'));
};


/**
 * @param {Function} callback Called when the user authorizes.
 *                            May not be called at all.
 */
klokantech.jekylledit.Auth.prototype.login = function(callback) {
  this.replaceWithSpinner_();
  goog.dom.appendChild(this.parentElement_, this.element_);

  this.checkLogin(goog.bind(function(success) {
    if (!goog.DEBUG && success) { //TODO
      goog.dom.removeNode(this.element_);
      callback();
    } else {
      this.showLoginBtn_(callback);
    }
  }, this));
};


/**
 * @param {Function} callback
 * @param {boolean=} opt_retry
 * @private
 */
klokantech.jekylledit.Auth.prototype.showLoginBtn_ =
    function(callback, opt_retry) {
  goog.dom.removeChildren(this.element_);
  if (opt_retry) {
    goog.dom.appendChild(this.element_,
        goog.dom.createDom(goog.dom.TagName.DIV, undefined,
            'Log in failed or not authorized!'));
  }
  var loginBtn = goog.dom.createDom(goog.dom.TagName.DIV, 'je-btn',
                                    opt_retry ? 'Retry' : 'Log in');
  goog.dom.appendChild(this.element_, loginBtn);
  goog.events.listen(loginBtn, goog.events.EventType.CLICK, function(e) {
    this.replaceWithSpinner_();
    var loginWindow = window.open(
        klokantech.jekylledit.BASE_URL + 'auth/widget',
        '_blank',
        'width=600,height=400'
        );
    var intervalId = setInterval(goog.bind(function() {
      try {
        if (loginWindow == null || loginWindow.closed) {
          clearInterval(intervalId);
          this.checkLogin(goog.bind(function(success) {
            if (success) {
              goog.dom.removeNode(this.element_);
              callback();
            } else {
              this.showLoginBtn_(callback, true);
            }
          }, this));
        }
      } catch (e) {}
    }, this), 500);
  }, false, this);
};


/**
 * @param {function(boolean)} callback
 */
klokantech.jekylledit.Auth.prototype.checkLogin = function(callback) {
  goog.net.XhrIo.send(klokantech.jekylledit.BASE_URL + 'auth/token',
      goog.bind(function(e) {
        var xhr = e.target;
        if (xhr.isSuccess()) {
          try {
            var response = xhr.getResponseJson();
            this.accessToken_ = response && response['accessToken'];
          } catch (e) {}
        }
        callback(goog.isString(this.accessToken_));
      }, this));
};


/**
 * @param {string} url Uri to make request to.
 * @param {Function=} opt_callback Callback function for when request is
 *     complete.
 * @param {string=} opt_method Send method, default: GET.
 * @param {ArrayBuffer|ArrayBufferView|Blob|Document|FormData|string=}
 *     opt_content Body data.
 * @param {Object=} opt_headers Map of headers to add to the request.
 */
klokantech.jekylledit.Auth.prototype.sendRequest =
    function(url, opt_callback, opt_method, opt_content, opt_headers) {
  if (!goog.isString(this.accessToken_)) {
    throw Error('Not authorized!');
  }
  var headers = goog.object.clone(opt_headers || {});
  headers['Authorization'] = 'Bearer ' + this.accessToken_;
  goog.net.XhrIo.send(klokantech.jekylledit.BASE_URL + url,
                      opt_callback, opt_method, opt_content, headers);
};
