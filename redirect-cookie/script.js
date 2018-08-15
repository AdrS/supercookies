window.onload = function() {
	var NUM_BITS = 10;
	function set_id(id, callback) {
		console.log('Setting user ID to...', id);
		// Fetch page (that should return a 301) so browser can cache redirect
		function set_bit(i) {
			var req = new XMLHttpRequest();
			req.onreadystatechange = function() {
				if(req.readyState === XMLHttpRequest.DONE && req.status === 200) {
					num_pending--;
					// See if all 1 bits have been encoded yet
					if(num_pending == 0) {
						console.log('Done setting ID');
						callback(id);
					}
				}
			}
			req.open('GET', '/testbit' + id);
			req.send();
		}
		// Inform server of user ID
		var req = new XMLHttpRequest();
		var num_pending = NUM_BITS;
		req.onreadystatechange = function() {
			if(req.readyState !== XMLHttpRequest.DONE) {
				return;
			}
			// After server has user ID, make requests so that brower
			// can see and cache 301 redirects
			if(req.status === 200) {
				for(var i = 0; i < NUM_BITS; ++i) {
					if((id >> i) & 1 === 1) {
						set_bit(i);
					} else {
						num_pending--;
					}
				}
			}
		}
		req.open('GET', '/setbits' + id);
		req.send();
	}
	// Retrieves ID and passes it to callback
	// ID is 0 if it has not been set before
	function get_id(callback) {
		console.log('Getting user ID...');
		var num_pending = NUM_BITS;
		var requests = [];
		var id = 0;
		for(var i = 0; i < NUM_BITS; ++i) {
			requests.push(new XMLHttpRequest());
			function handle(num) {
				return function() {
					if(requests[num].readyState !== XMLHttpRequest.DONE) {
						return;
					}
					if(requests[num].status === 200) {
						if(requests[num].responseText === '1') {
							id = id | (1<<num);
						}
					}
					// TODO: handler errors
					num_pending--;
					if(num_pending <= 0) {
						callback(id);
					}
				}
			}
			requests[i].onreadystatechange = handle(i);
			requests[i].open('GET', '/testbit' + i);
			requests[i].send();
		}
	}
	get_id(function(id) {
		console.log(id);
		// ID has not been set
		if(id === 0) {
			// Generate random ID 	
			id = Math.floor(Math.random() * (1<<NUM_BITS));
			// Inform server of ID and store ID using the redirect cache
			set_id(id, function() { console.log("done"); });
		}
	});
}
