/**
 * SMS Communication Protocol for Data Updates
 * @author Matthew MacLennan matt@thevertigo.com
 * @requires {@link https://code.google.com/p/crypto-js/#MD5}
 */

/**
 * Partitions 'data update' command into SMS compatible sizes
 * (< 144 characters).
 * @param {string} command - command to be executed on remote server
 * @returns {string[]} bodies - command partitioned into strings to be
 * 				sent via sms
 */
function partitionMessage(command) {
    var cmdLength = command.length;
    var cmdComponents = [];
    // if size fits into one sms
    if (cmdLength <= 80) {
	cmdComponents.push(command);
    } 
    // message has to be split amongst multiple SMS
    else {
	lastComponent = command.slice(-113); // message in header with hash
	var newLength = cmdLength - 113;
	var endIndex = -113; //first char in regular header/message
	var beginIndex = -114 - 144;
	var cmdComponent;
	while (newLength > 0) {
	    cmdComponent = command.slice(beginIndex, endIndex);
	    cmdComponents.unshift(cmdComponent);
	    newLength = newLength - 144;
	    endIndex = beginIndex;
	    beginIndex = endIndex - 144;
	}
	cmdComponents.push(lastComponent);
    }
    return cmdComponents;
}

/**
 * Create's an array of SMS messages that encode the data update
 * to be sent to a receiving server.
 *
 * @param {object[]} models - array of models to be updated on server
 * @param {Number[]} actions - array of actions to take on models.
 * @returns {string[]} array of strings to be sent via SMS
 */
function prepareSms(models, actions) {

    var preString = {};
    // stringify each object/model
    for (i = 0; i < actions.length; i++) {
	if (preString.hasOwnProperty(actions[i])) {
	    preString[actions[i]].push(JSON.stringify(models[i], null, 0));
	}
	else {
	    preString[actions[i]] = []
	    preString[actions[i]].push(JSON.stringify(models[i], null, 0));
	}
    }
    var finalMessages = [];
    
    // models and actions stringfied
    var string = JSON.stringify(preString);
    var hash = CryptoJS.MD5(string);
    var hashString = hash.toString(CryptoJS.enc.Hex);
    // cutting up message
    var cmdComponents = partitionMessage(string);
    var numMessages = cmdComponents.length;
    var seq;
    var seqString;
    var tseq;
    var seqAndHash;
    var fullMessage;
    // if only one message setup finalheader with hash and return
    if (numMessages == 1) {
	var seqInfo = '0001';
	seqAndHash = seqInfo.concat(hashString);
	fullMessage = seqAndHash.concat(string);
	finalMessages.push(fullMessage);
	return finalMessages;
    }
    //string of tseq
    var tseqString = ("00" + numMessages).substr(-2,2);

    for (i = 0; i < numMessages; i ++) {
	if (i == (numMessages - 1)) {
	    seq = i;
	    seqString = ("00" + seq).substr(-2,2);
	    seqAndTotal = seqString.concat(tseqString);
	    seqAndHash = seqAndTotal.concat(hashString);
	    fullMessage = seqAndHash.concat(cmdComponents[i]);
	    finalMessages.push(fullMessage);
	}
	else {
	    seq = i;
	    seqString = ("00" + seq).substr(-2,2);
	    seqAndTotal = seqString.concat(tseqString);
	    fullMessage = seqAndTotal.concat(cmdComponents[i]);
	    finalMessages.push(fullMessage);
	}
    }

    return finalMessages;
}
