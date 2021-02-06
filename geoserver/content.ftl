<ul>
<#list features as feature>
  <li><b>Type: ${type.name}</b> (id: <em>${feature.fid}</em>):
  <ul>
  <#list feature.attributes as attribute>
    <#if !attribute.isGeometry>
      <#if attribute.value?has_content>
        <#if attribute.name == "@id">
          <li>${attribute.name}: <a target='osm' href='https://www.openstreetmap.org/${attribute.value}'>${attribute.value}</a></li>
        <#else>
          <li>${attribute.name}: ${attribute.value}</li>
        </#if>
      </#if>
    </#if>
  </#list>
  </ul>
  </li>
</#list>
</ul>