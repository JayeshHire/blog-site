import {editor, articleInfoEditor} from './editor_obj.js'

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

async function get_current_article_id(){
    try {
        const response = await fetch(
            "http://127.0.0.1:8000/article/id", {method: "GET"}
        );

        if (!response.ok){
            console.log(response.status) ;
        } else {
            const data = await response.json() ;
            return data.article_id ;
        }
    } catch (err) {
        console.log(err) ;
    }
}

const saveBtn = document.getElementById("save-btn") ;
saveBtn.addEventListener("click", async () => {
    editor.save().then(async (outputData) => {
        console.log("output data:")

        const article_id = await get_current_article_id();

        // below values should be replaced according to the user session data
        // outputData.logged_in_session_id = "abcdf" ;
        // outputData.browser_session_id = "dbshfg" ;
        outputData.article_id = article_id ;
        console.log(JSON.stringify(outputData));
        console.log("hello") ;
        post_data(outputData, "http://127.0.0.1:8000/editorjs/save/article/body");
    }).catch((err) => {
        console.log(err);
    }) ;
}); 

const saveArtBtn = document.getElementById("save-article-head") ;
saveArtBtn.addEventListener("click", async () => {
    articleInfoEditor.save().then(async (outputData) => {
        const article_id = await get_current_article_id()
        outputData.article_id = article_id ;
        console.log(JSON.stringify(outputData)) ;
        post_data(outputData, "http://127.0.0.1:8000/editorjs/save/article/head") ;
    }).catch((err) => {
        console.log(err) ;
    }) ;
}) ;

const testBtn = document.getElementById("test-btn");
testBtn.addEventListener("click", () => {
    console.log("pressed test") ;
    fetch("/").then((res) => {
        // console.log(res.body) ;
        return res.text() ;
    }).then((res) => {
        console.log(res) ;
    }) ;
});


// preventing creation of new block on enter
const articleDataContainer = document.getElementById("article_info_editor");

articleDataContainer.addEventListener("keydown", (e) => {
    if (e.key == "Enter") {
        e.preventDefault() ;
        e.stopPropagation();
    }
}, true) ;

async function get_article_head_data(){
    const url = "http://127.0.0.1:8000/load/article/head/previous_state" ;

    try {
        const response = await fetch(
            url,
            {
                method: "GET"
            }
        ) ;

        if (!response.ok){
            console.log(response.status)
        } else {
            const responseData = await response.json() ;
            return responseData ;
        }
    } catch (err) {
        console.log(err) ;
    }
    
}

async function get_article_body_data() {
    const url = "http://127.0.0.1:8000/load/article/body/previous_state" ;

    try {
        const response = await fetch(
            url,
            {
                method: "GET"
            }
        ) ;

        if (!response.ok){
            console.log(response.status)
        } else {
            const responseData = await response.json() ;
            return responseData ;
        }
    } catch (err) {
        console.log(err) ;
    }
}

async function populate_previous_state(){
    const article_head = await get_article_head_data() ;
    const article_body = await get_article_body_data() ;

    if (article_head) {
        articleInfoEditor.isReady.then(() => {
            console.log(article_head) ;
            articleInfoEditor.render(article_head).then(() => {
                console.log("data saved successfully");
            })
            .catch((err) => {
                console.log(err) ;
            });
        }).catch(err => {
            console.log("initialization failed") ;
        }) ;
    }

    if (article_body) {
        editor.isReady.then(() => {
            console.log(article_body) ;
            editor.render(article_body).then(() => {
                console.log("populated the data successfully") ;
            }).catch((err) => {
                console.log(err) ;
            }) ;
        }).catch((err) => {
            console.log("editor not ready error") ;
            console.log(err) ;
        }) ;
    }
    
}

populate_previous_state().then(() => {
    console.log("data has been populated");
}) ;