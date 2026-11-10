/** Browser-only simulator SDK. Never compatible with the native GoPay SDK. */
export function createMerchantBridge({merchantOrigin}) {
  if (new URL(merchantOrigin).origin !== merchantOrigin) throw new Error('Expected exact merchant origin');
  return {
    getAccessToken() {
      return new Promise((resolve, reject) => {
        if (window.parent === window) return reject(new Error('CONTAINER_REQUIRED'));
        const request_id = crypto.randomUUID();
        const cleanup = () => { clearTimeout(timer); window.removeEventListener('message', receive); };
        const receive = event => {
          if (event.origin !== merchantOrigin || event.source !== window.parent) return;
          const data = event.data;
          if (!data || data.type !== 'miniapp.auth.response' || data.request_id !== request_id) return;
          if (data.error && typeof data.error.code === 'string') { cleanup(); reject(new Error(data.error.code)); }
          else if (data.data && typeof data.data.access_token === 'string' && data.data.token_type === 'Bearer' && typeof data.data.expires_in === 'number' && typeof data.data.merchant_code === 'string') {
            cleanup(); resolve(data.data);
          }
        };
        const timer = setTimeout(() => { cleanup(); reject(new Error('BRIDGE_TIMEOUT')); }, 10000);
        window.addEventListener('message', receive);
        window.parent.postMessage({type:'miniapp.auth.request', request_id}, merchantOrigin);
      });
    }
  };
}
