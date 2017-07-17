tpl_dict = {
    
'meta_docstring':"""sets markdown main titles (with one #) as their own slides, 
remove latex tags and code cells """,

"overwrite":['notebook_all', 'notebook_input_markdown_pre', 
'notebook_input_markdown','html_body_end',
'notebook_input_code','notebook_input_code_pre','notebook_input_code_post'],

'notebook_all':'{{ super() }}',

'notebook_input_code_pre':r"""
""",
'notebook_input_code_post':r"""
""",
'notebook_input_code':r"""
""",

'notebook_input_markdown':r"""
{{ cell.source | remove_tex_tags | markdown2html | strip_files_prefix }}
""",

'html_body_start':r"""

""",

'notebook_input_markdown_pre':r"""
{%- if cell.source[0] == '#' -%}
    {%- if cell.source[1] == '#' -%}
        {%- if cell.source[2] == '#' -%}

        {%- else -%}
</section>
<section>
        {%- endif -%}
    {%- else -%}
</section>
<section>
    {%- endif -%}
{%- endif -%}
<div class="input_markdown">
<div class="cell border-box-sizing text_cell rendered">
<div class="inner_cell">
<div class="text_cell_render border-box-sizing rendered_html">
""",

'html_body_end':r"""
</section>
</div>
</div>

<script>

require(
    {
      // it makes sense to wait a little bit when you are loading
      // reveal from a cdn in a slow connection environment
      waitSeconds: 15
    },
    [
      "{{resources.reveal.url_prefix}}/lib/js/head.min.js",
      "{{resources.reveal.url_prefix}}/js/reveal.js"
    ],

    function(head, Reveal){

        // Full list of configuration options available here: https://github.com/hakimel/reveal.js#configuration
        Reveal.initialize({
            controls: true,
            progress: true,
            history: true,

            theme: Reveal.getQueryHash().theme, // available themes are in /css/theme
            transition: Reveal.getQueryHash().transition || 'linear', // default/cube/page/concave/zoom/linear/none

            // Optional libraries used to extend on reveal.js
            dependencies: [
                { src: "{{resources.reveal.url_prefix}}/lib/js/classList.js",
                  condition: function() { return !document.body.classList; } },
                { src: "{{resources.reveal.url_prefix}}/plugin/notes/notes.js",
                  async: true,
                  condition: function() { return !!document.body.classList; } }
            ]
        });

        var update = function(event){
          if(MathJax.Hub.getAllJax(Reveal.getCurrentSlide())){
            MathJax.Hub.Rerender(Reveal.getCurrentSlide());
          }
        };

        Reveal.addEventListener('slidechanged', update);

        var update_scroll = function(event){
          $(".reveal").scrollTop(0);
        };

        Reveal.addEventListener('slidechanged', update_scroll);
        
        Reveal.configure({ slideNumber: 'c/t' });

    }
);
</script>
"""

}

