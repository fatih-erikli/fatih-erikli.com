import yaml
import markdown
import uuid
import codecs


def extend(base='base.html', title='Untitled', content='\n', date=None):
  base_template = open(base).read()
  return base_template % {
    'content': content,
    'random': uuid.uuid4().hex,
    'title': title,
    'date': date
  }

def render_markdown(content):
  return markdown.markdown(content, extensions=['fenced_code', 'codehilite'])

def write_post(post):
  file_name = post['file']
  rendered_markdown = render_markdown(post['content'])
  rendered_blog_post = extend(base='blog-detail.template.html',
                              content=rendered_markdown,
                              title=post['title'],
                              date=post['date']
                              )
  rendered_base = extend(
      base='base.html',
      title=post['title'],
      content=rendered_blog_post
  )
  with codecs.open(file_name.replace('.md', '.html'), 'w', 'utf-8') as file:
      file.write(rendered_base)

yaml_content = open('blog.yaml').read()
meta_data = (yaml.load(yaml_content, Loader=yaml.FullLoader))

posts = meta_data.get('posts')
posts_html = []
for (index, post) in enumerate(posts):
  file_name = post['file']
  content = open(file_name).read()
  post['content'] = content
  write_post(post)
  post_preview = render_markdown(content.split('\n\n')[0])
  posts_html.append(
      '''
      <article tabindex="%(tab_index)s">
        <h3><a role="link" href="%(url)s">%(title)s</a></h3>
        <div class="date-time">%(date)s</div>
        <div class="post-preview">%(post_preview)s</div>
      </article>
      ''' % {
          'post_preview': post_preview,
          'url': post['file'].replace('.md', '.html'),
          'title': post['title'],
          'date': post['date'],
          'tab_index': len(posts) - index
      }
  )

rendered_index_contents = extend(
  base='base.html',
  title='Fatih Erikli',
  content=extend("index.template.html", content='\n'.join(posts_html))
)

with open('index.html', 'w') as index_file:
    index_file.write(rendered_index_contents)
