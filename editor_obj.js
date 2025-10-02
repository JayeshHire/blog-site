import EditorJS from '@editorjs/editorjs';
import Header from '@editorjs/header'; 
import EditorjsList from '@editorjs/list'; 

const editor = new EditorJS({
    holderId: 'editor',

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
   }
}) ;


export default editor ;