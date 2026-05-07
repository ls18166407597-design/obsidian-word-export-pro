-- Obsidian to Word Expert Lua Filter
-- Optimized for Academic Writing and Professional Layouts

local function stringify(value)
  if value == nil then return '' end
  return pandoc.utils.stringify(value)
end

-- Check if a block already has a custom-style attribute
local function has_custom_style(el)
  return el.attributes and el.attributes['custom-style'] ~= nil
end

-- Create a styled paragraph (using Div with custom-style for maximum Word compatibility)
local function make_styled_para(content, style_name)
  local inlines = content
  if type(content) == 'table' and content.t == 'Para' then
    inlines = content.content
  end
  return pandoc.Div(
    { pandoc.Para(inlines) },
    pandoc.Attr('', {}, { { 'custom-style', style_name } })
  )
end


-- Main processing logic
function Pandoc(doc)
  local blocks = doc.blocks
  local output = {}
  local i = 1

  while i <= #blocks do
    local block = blocks[i]
    local next_block = blocks[i + 1]

    -- 1. Handle Images followed by Captions
    -- If current block is a Para containing an Image and next block starts with "图" or "Figure"
    if block.t == 'Para' and #block.content == 1 and block.content[1].t == 'Image' then
      table.insert(output, block)
      if next_block and (next_block.t == 'Para' or next_block.t == 'Plain') then
        local text = stringify(next_block.content)
        if (text:match('^图%s?%d+') or text:match('^Figure%s?%d+')) and not has_custom_style(next_block) then
          table.insert(output, make_styled_para(next_block.content, 'ImageCaption'))
          i = i + 2
          goto continue
        end
      end
    end

    -- 2. Handle Tables followed by Notes
    -- If current block is a Table and next block starts with "注：" or "Note:"
    if block.t == 'Table' then
      table.insert(output, block)
      if next_block and (next_block.t == 'Para' or next_block.t == 'Plain') then
        local text = stringify(next_block.content)
        if (text:match('^注[：:]') or text:match('^Note[：:]')) and not has_custom_style(next_block) then
          table.insert(output, make_styled_para(next_block.content, 'TableNote'))
          i = i + 2
          goto continue
        end
      end
    end

    -- 3. Handle Table Captions (Paragraphs starting with "表" or "Table" above a table)
    if (block.t == 'Para' or block.t == 'Plain') and next_block and next_block.t == 'Table' then
      local text = stringify(block.content)
      if (text:match('^表%s?%d+') or text:match('^Table%s?%d+')) and not has_custom_style(block) then
        table.insert(output, make_styled_para(block.content, 'TableCaption'))
        i = i + 1
        goto continue
      end
    end

    -- 4. Code Blocks styling
    if block.t == 'CodeBlock' and not has_custom_style(block) then
      block.attributes['custom-style'] = 'SourceCode'
      table.insert(output, block)
      i = i + 1
      goto continue
    end

    -- Default: keep as is
    table.insert(output, block)
    i = i + 1

    ::continue::
  end

  doc.blocks = output
  return doc
end
