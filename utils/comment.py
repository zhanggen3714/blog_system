def comment_tree(comment_list):
    comment_str = '<div class="comment">'
    for row in comment_list:
        tp1 = '<div class="content">%s</div>' % (row['content'])
        comment_str += tp1
        if row['child']:
            childstr = comment_tree(row['child'])
            comment_str+=childstr
    comment_str += '</div>'
    return comment_str
