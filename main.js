import editor from './editor_obj.js'

async function post_data(data, url){
    console.log("entering post function") ;
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data) 
        }) ;

        if (!response.ok){
            console.log(response.status) ;
        } else {
            const responseData = await response.json();
            console.log(responseData) ;
        }
    }
    catch (err) {
        console.log(err);
    }
}

const saveBtn = document.getElementById("save-btn") ;
saveBtn.addEventListener("click", async () => {
    editor.save().then((outputData) => {
        console.log("output data:")

        // below values should be replaced according to the user session data
        outputData.logged_in_session_id = "abcdf" ;
        outputData.browser_session_id = "dbshfg" ;

        console.log(outputData);
        console.log("hello") ;
        post_data(outputData, "http://127.0.0.1:8000/editorjs");
    }).catch((err) => {
        console.log(err);
    }) ;
}); 


const testBtn = document.getElementById("test-btn");
testBtn.addEventListener("click", () => {
    console.log("pressed test") ;
    fetch("/").then((res) => {
        // console.log(res.body) ;
        return res.text() ;
    }).then((res) => {
        console.log(res) ;
    }) ;
})
