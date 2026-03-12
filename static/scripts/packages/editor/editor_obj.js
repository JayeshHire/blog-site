import EditorJS from '@editorjs/editorjs';
import Header from '@editorjs/header'; 
import EditorjsList from '@editorjs/list'; 
import Paragraph from '@editorjs/paragraph';

export const editor = new EditorJS({
    holderId: 'editor',
    placeholder: 'Note down your own thoughts here.',
    tools: {
        header: {
            class: Header,
            inlineToolbar: true,
            levels: [2, 3, 4],
            defaultLevel: 3
        },
        list: {
            class: EditorjsList,
            inlineToolbar: true
        }
    },

    onReady: () => {
      console.log('Editor.js is ready to work!')
   },

   onChange: (api, event) => {
        api.saver.save().then((outputData) => {
            console.log("changed editor data") ;
            console.log(outputData) ;
        })
   }
}) ;

export const articleInfoEditor = new EditorJS({
    holder: "article_info_editor",
    tools: {
        title: {
            class: Header,
            config: {
                placeholder: "Enter the title of the article",
                levels: [1],
                defaultLevel: 1
            },
            toolbox: {
                title: "Title"
            }
        },
        subtitle: {
            class: Header,
            config: {
                placeholder: "Enter the subtitle of the article here.",
                levels: [3],
                defaultLevel: 3
            },
            toolbox: {
                title: "Subtitle"
            }
        },
        // hiding the default tool text
        paragraph: {
            class: Paragraph,
            toolbox: false 
        }
    },
    defaultBlock: "title",
    data: {
        blocks: [
            {
                type: "title",
                data: {}
            },
            {
                type: "subtitle",
                data: {}
            }
        ]
    },
    onChange: (api, event) => {
        api.saver.save().then((outputdata) => {
            if (outputdata.blocks.length > 2) {
                console.log("maximum block limit reached.") ;
            }
        });

        if (event.length > 1 && event[1].type == "block-added") {
            const blockIndex = event[1].detail.index ;
            const content = event[1].detail.target.holder.innerText ;
            const block_id = event[1].detail.target.id ;
            if (blockIndex == 0){
                api.blocks.delete(0) ;
                api.blocks.insert('title', {text: content}, {}, 0, true) ;
            } else if (blockIndex == 1){
                api.blocks.insert('subtitle', {text: content}, {}, 1, true) ;
                api.blocks.delete(2) ;
            }
        }

        if (event.type == 'block-added') {
            const blockIndex = event.detail.index ;
            api.blocks.delete(blockIndex) ;
        }
    }
}) ;


// export default editor ;
// export default articleInfoEditor ;