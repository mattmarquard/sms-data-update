/**
 * SMS Communication Protocol for Data Updates
 * @author Matthew MacLennan matt@thevertigo.com
 * @requires {@link https://code.google.com/p/crypto-js/#MD5}
 */

/**
 * Partitions 'data update' command into SMS compatible sizes for protocol
 * (145 characters).
 * @param {string} command - command to be executed on remote server
 * @returns {string[]} bodies - command partitioned into strings to be
 * 				sent via sms
 */
function partitionMessage(command) {
    var lastMsgLength = 113;
    var regMsgLength = 144;
    console.log('prepartition');
    console.log(command.length);
    console.log(command);
    var cmdLength = command.length;
    var cmdComponents = [];
    // if size fits into one sms
    if (cmdLength <= lastMsgLength) {
	cmdComponents.push(command);
    } 
    // message has to be split amongst multiple SMS
    else {
	lastComponent = command.slice(-lastMsgLength); // message in header with hash
	var newLength = cmdLength - lastMsgLength; 
	var endIndex =  -lastMsgLength; //first char in regular header/message
	var beginIndex = -114 - regMsgLength; //114 is first index after last component.
	var cmdComponent;
	while (newLength > 0) {
	    cmdComponent = command.slice(beginIndex, endIndex);
	    cmdComponents.unshift(cmdComponent);
	    newLength = newLength - regMsgLength;
	    endIndex = beginIndex;
	    beginIndex = endIndex - regMsgLength;
	}
	cmdComponents.push(lastComponent);
    }
    return cmdComponents;
}


/**
 * Create JSON object of models and associated actions.
 *
 * @param {object[]} models - array of models to be updated on server
 * @param {Number[]} actions - array of actions to take on models.
 * @returns {object} JSON object of models and actions to take on them.
 */
function matchModelsToActions(models, actions) {

    var preString = {}
    for (i = 0; i < actions.length; i++) {
	if (preString.hasOwnProperty(actions[i])) {
	    preString[actions[i]].push(models[i]);
	}
	else {
	    preString[actions[i]] = []
	    preString[actions[i]].push(models[i]);
	}
    }
    return preString;


/**
 * Create's an array of SMS messages that encode the data update
 * to be sent to a receiving server.
 *
 * @param {object[]} models - array of models to be updated on server
 * @param {Number[]} actions - array of actions to take on models.
 * @returns {string[]} array of strings to be sent via SMS
 */
function prepareSms(models, actions) {

    var preString = matchModelsToActions(models, actions);
    var string = JSON.stringify(preString, null, 0);
    var hash = CryptoJS.MD5(string);
    var hashString = hash.toString(CryptoJS.enc.Hex);
    // cutting up message
    var cmdComponents = partitionMessage(string);
    var finalMessages = [];
    var numMessages = cmdComponents.length;
    var seq;
    var seqString;
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
    var tSeqString = ("00" + numMessages).substr(-2,2);

    for (i = 0; i < numMessages; i ++) {
	if (i == (numMessages - 1)) {
	    seq = i;
	    seqString = ("00" + seq).substr(-2,2);
	    seqAndTotal = seqString.concat(tSeqString);
	    seqAndHash = seqAndTotal.concat(hashString);
	    fullMessage = seqAndHash.concat(cmdComponents[i]);
	    finalMessages.push(fullMessage);
	}
	else {
	    seq = i;
	    seqString = ("00" + seq).substr(-2,2);
	    seqAndTotal = seqString.concat(tSeqString);
	    fullMessage = seqAndTotal.concat(cmdComponents[i]);
	    finalMessages.push(fullMessage);
	}
    }
    console.log(finalMessages);
    return finalMessages;
}
