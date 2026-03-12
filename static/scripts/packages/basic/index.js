const url = "http://127.0.0.1:8000" ;

const get_markup = async (path) => {
    // string of the path should start with '/'
    console.log("inside the get_markup function") ;
    const uri = `${url}${path}` ;
    console.log(uri) ;
    try{
        const response = await fetch(
            uri,
            {
                method: "GET"
            }
        ) ;
        
        if (!response.ok) {
            console.log(response);
        } else {
            const data = await response.json() ;
            return data ;
        }
    } catch (err) {
        console.log(err);
    }
}

const get_signup_form = async () => {
    const path = "/markup/form/signup" ;

    const data = await get_markup(path) ;
    return data.signup_form ;
}

const get_signin_form = async () => {
    const path = "/markup/form/signin" ;

    const data = await get_markup(path) ;
    return data.signin_form ; 
}

const get_logout_form = async () => {
    const path = "/markup/form/logout" ;

    const data = await get_markup(path) ;
    return data.logout_form ;
}

const submitForm = async () => {
    const parentEle = document.querySelector(".options-content-window");
    // const optionContentWin = document.querySelector(".options-content-window") ;
    parentEle.addEventListener("submit", async (e) => {
        e.preventDefault() ;

        const form = e.target ;
        const data = new FormData(form) ;

        console.log(data) ;
        console.log(Object.keys(data).length === 0) ;
        let res ;
        if (form.id === "form-logout") {
            res = await fetch(form.action, {
                method: form.method 
            });
        } else {
            res = await fetch(form.action, {
                method: form.method || "POST",
                body: data,
            });
        }
        
        if (res.ok){
            parentEle.style.visibility = "hidden" ;
        }

        window.location.reload() ;

        controlOptionsVisibility().then(() => {
            console.log("changed the visibility of options") ;
        }) ;
    }) ;
}

const optionsFunctionality = async () => {
    const body = document.body ;

    // changing the visibility of the general options list
    const optionIcon = document.querySelector(".option-icon");
    const optionListEle = document.querySelector(".options");
    optionListEle.style.visibility = "hidden" ;
    optionIcon.addEventListener("click", () => {
        let curr = optionListEle.style.visibility ;
        if (curr == "hidden") {
            optionListEle.style.visibility = "visible" ;
        } else if (curr == "visible") {
            optionListEle.style.visibility = "hidden" ;
        }
    }) ;

    // changing the visibility of the profile options list
    const profileIconEle = document.querySelector(".profile-icon img") ;
    const profileOptionListEle = document.querySelector(".profile-option-list");
    profileOptionListEle.style.visibility = "hidden" ;
    profileIconEle.addEventListener("click", () => {
        let curr_visibility = profileOptionListEle.style.visibility ;
        if (curr_visibility == "hidden") {
            profileOptionListEle.style.visibility = "visible" ;
        } else if  (curr_visibility == "visible") {
            profileOptionListEle.style.visibility = "hidden" ;
        }
    });

    // showing the detail info for each item
    const signupForm =  await get_signup_form() ;
    const signinForm = await get_signin_form() ;
    const logoutForm = await get_logout_form() ;
    const optionIdTextMp = new Map() ;
    optionIdTextMp.set('op-drafts', 
        'this is the list of drafts written by you\ndraft 1\n draft 2\ndraft 3'
    ) ;
    optionIdTextMp.set('op-pub-articles', 
        'this is the list of your published articles\narticle 1\n article 2\article 3'
    ) ;
    optionIdTextMp.set('op-comm-articles',
        'this is the list of community articles published by other creators\narticle 1\n article 2\article 3'
    ) ;
    optionIdTextMp.set('op-profile-setting',
        'this is the list of profile settings read by the logged in user.'
    ) ;
    optionIdTextMp.set('op-logout', 
        logoutForm
    ) ;
    optionIdTextMp.set('op-signup', 
        signupForm
    ) ;
    optionIdTextMp.set('op-login',
        signinForm
    ) ;

    const opContentWin = document.querySelector(".options-content-window") ;
    opContentWin.style.visibility = "hidden" ;

    // clicking anywhere on the screen should remove the options
    body.addEventListener("click", (event) => {
        if (!optionIcon.contains(event.target) && 
        !profileIconEle.contains(event.target) && 
        !opContentWin.contains(event.target)
    ) {
            if (profileOptionListEle.style.visibility == "visible" ||
                optionListEle.style.visibility == "visible"
            ) {
                if (profileOptionListEle.contains(event.target) || 
                optionListEle.contains(event.target) || 
                opContentWin.contains(event.target)
            ){
                    opContentWin.style.visibility = "visible" ;
                } else {
                    opContentWin.style.visibility = "hidden" ;
                }
            } else {
                if (!opContentWin.contains(event.target)){
                    opContentWin.style.visibility = "hidden" ;
                }
            }
            profileOptionListEle.style.visibility = "hidden" ;
            optionListEle.style.visibility = "hidden" ;
        } 

    }) ;

    // getting the content to be populated in the 
    // option content window.
    for (const [ele_id, text] of optionIdTextMp){
        const ele = document.getElementById(ele_id) ;
        const opContentWinChild = document.querySelector(".options-content-window div") ;
        ele.addEventListener("click", ()=> {
            opContentWin.style.visibility = "visible" ;
            opContentWinChild.innerHTML = text ;
        }) ;
    }
}

/*
Get the status of the user for the current browser session.
The user can be logged in or logged out. Get that data for 
the user.
*/
async function is_user_logged_in(){
    const url = "/user/status/is_logged_in"
    const response = await fetch(
        url,
        {
            method: "GET"
        } 
    ) ;

    if (!response.ok) {
        console.log(response) ;
    } else {
        const status = await response.json() ;
        return status.is_logged_in ;
    }
}


const controlOptionsVisibility = async () => {
    /*
    This function will hide the options 
    if the user is not logged in.
    If the user is logged in then it will show all the options. 
    */
    console.log("inside the controlOptionsVisibility function") ;
    const status = await is_user_logged_in() ;
    console.log(`status: ${status}`) ;
    if (status) {
        const optionBox = document.querySelector(".option-box") ;
        const visibleIDs = ['op-logout', 'op-profile-setting'] ;
        const hiddenIDs = ['op-login', 'op-signup'] ;
        optionBox.style.visibility = "visible" ;
        visibleIDs.map((id) => {
            const ele = document.getElementById(id) ;
            ele.style.display = "" ;
        }) ;
        hiddenIDs.map((id) => {
            const ele = document.getElementById(id) ;
            ele.style.display = "none";
        }) ;
    } else {
        const optionBox = document.querySelector(".option-box") ;
        const hiddenIDs = ['op-logout', 'op-profile-setting'] ;
        const visibleIDs = ['op-login', 'op-signup'] ;
        optionBox.style.visibility = "hidden" ;
        visibleIDs.map((id) => {
            const ele = document.getElementById(id) ;
            ele.style.display = "" ;
        }) ;
        hiddenIDs.map((id) => {
            const ele = document.getElementById(id) ;
            ele.style.display = "none";
        }) ;
    }
} ;

optionsFunctionality() ;
controlOptionsVisibility() ;
submitForm() ;