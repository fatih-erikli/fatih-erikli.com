import yaml
import markdown
import uuid
import codecs


def extend(base='base-grid.html', title='Untitled', content='\n', date=None, others=''):
  base_template = open(base).read()
  return base_template % {
    'content': content,
    'random': uuid.uuid4().hex,
    'title': title,
    'date': date,
    'navigation': open('navigation.html').read(),
    'others': others
  }


def render_markdown(content):
  return markdown.markdown(content, extensions=['fenced_code'])


def render_post_preview(post):
  content = open(post['file']).read()
  post_preview = render_markdown(content.split('###')[0])
  return '''
    <article role="listitem" aria-posinset="%(post_inset)s" tabindex="%(tab_index)s">
      <h3 aria-label="Title"><a role="link" href="%(url)s">%(title)s</a></h3>
      <time>%(date)s</time>
      <div aria-label="Description" role="contentinfo" class="post-preview">%(post_preview)s</div>
    </article>
    ''' % {
      'post_inset': index,
      'post_preview': post_preview,
      'url': post['file'].replace('.md', '.html'),
      'title': post['title'],
      'date': post['date'],
      'tab_index': 0 - len(posts) - index,
      'navigation': open('navigation.html').read()
    }

def write_post(post, links):
  file_name = post['file']
  content = open(file_name).read()
  rendered_markdown = render_markdown(content)
  rendered_blog_post = extend(base='blog-detail.template.html',
                              content=rendered_markdown,
                              title=post['title'],
                              date=post['date'],
                              others=links
                              )
  rendered_base = extend(
    base='base-grid.html',
    title=post['title'],
    content=rendered_blog_post
  )
  with codecs.open(file_name.replace('.md', '.html'), 'w', 'utf-8') as file:
    file.write(rendered_base)

yaml_content = open('blog.yaml').read()
meta_data = (yaml.load(yaml_content, Loader=yaml.FullLoader))

posts = meta_data.get('posts')
posts_html = [
  
]
for (index, post) in enumerate(posts):
  file_name = post['file']
  links = map(render_post_preview, posts[index+1:index+4])
  links = '\n'.join(links)
  write_post(post, links='<div aria-label="blog posts" class="other-posts" role="list" tabindex="-1">%s</div>' % links)
  posts_html.append(render_post_preview(post))

rendered_index_contents = extend(
  base='base-grid.html',
  title='Fatih Erikli',
  content=extend("index-grid.template.html", content='\n'.join(posts_html))
)

with open('index.html', 'w') as index_file:
  index_file.write(rendered_index_contents)
